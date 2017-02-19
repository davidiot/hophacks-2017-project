from rest_framework.response import Response
from .models import Link, Sector, Rule, Charity, Suggestion, Donation
from .serializers import LinkSerializer, CharitySerializer, \
    SuggestionSerializer, DonationSerializer, UserSerializer
from rest_framework.decorators import api_view
import datetime
import requests
import json
from django.http import HttpResponse

sector_map = {
    'Clothing': 'Clothing',
    'Lodging': 'Travel',
    'Food': 'Food',
    'Health': 'Health',
    'Tech': 'Technology'
}

charity_map = {
    'Clothing': 'Clothing',
    'Travel': 'Environment',
    'Food': 'Food',
    'Health': 'Health',
    'Technology': 'Tech'
}

api_key = '52f69545ffa7fffb30dc369ac3103f7f'


@api_view(['GET'])
def get_my_id(request):
    current_user = request.user
    serializer = UserSerializer(
        current_user,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['POST'])
def make_donation(request):
    body = request.data
    current_user = request.user
    charity_id = body['charity_id']
    charity = Charity.objects.get(id=charity_id)
    amount = body['amount']

    purchase_url = 'http://api.reimaginebanking.com/accounts/{}' \
                   '/purchases?key={}'\
        .format(current_user.profile.charity_account_id, api_key)

    date = datetime.datetime.now().strftime("%Y-%m-%d")

    payload = {
        "merchant_id": charity.merchant_id,
        "medium": "balance",
        "purchase_date": date,
        "amount": amount,
        "description": "A donation of ${} made to {} from {}".format(
            amount,
            charity.name,
            current_user.username)
    }

    purchase_response = requests.post(
        purchase_url,
        data=json.dumps(payload),
        headers={'content-type': 'application/json'}
    ).json()

    donation = Donation.objects.create(
        user=current_user,
        charity=charity,
        purchase_id=purchase_response["objectCreated"]["_id"]
    )

    serializer = DonationSerializer(
        donation,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
def get_spending(request):
    spending = calculate_spending(request)
    return Response(spending)


def calculate_spending(request):
    spending = {}
    links = get_links_from_c1(request, serialize=False)
    for link in links:
        url = 'http://api.reimaginebanking.com/purchases/{}?key={}'.format(
            link.purchase_id, api_key)
        purchase = requests.get(
            url,
            headers={'content-type': 'application/json'},
        ).json()
        try:
            spending[link.sector.name] = \
                spending[link.sector.name] + purchase['amount']
        except KeyError:
            spending[link.sector.name] = purchase['amount']

    for sector_name in spending:
        spending[sector_name] = round(spending[sector_name], 2)

    return spending


@api_view(['GET'])
def get_displayed_suggestions(request):
    spending = calculate_spending(request)
    output = []
    for sector_name in spending:
        sect = Sector.objects.get(name=sector_name)
        na = float(sect.national_average)
        output.extend(
            Suggestion.objects.filter(
                sector=sect,
                threshold__lte=((spending[sector_name] - na) / na * 100)
            )
        )
    serializer = SuggestionSerializer(
        output,
        context={'request': request},
        many=True
    )
    return Response(serializer.data)


@api_view(['GET'])
def get_charities_by_name(request, sect):
    sector = Sector.objects.get(
        name=sect
    )
    charities = Charity.objects.filter(sector=sector)
    serializer = CharitySerializer(
        charities,
        context={'request': request},
        many=True
    )
    return Response(serializer.data)


@api_view(['GET'])
def get_charities_by_id(request, id):
    sector = Sector.objects.get(
        id=id
    )
    charities = Charity.objects.filter(sector=sector)
    serializer = CharitySerializer(
        charities,
        context={'request': request},
        many=True
    )
    return Response(serializer.data)


@api_view(['GET'])
def pull_purchases(request):
    return get_links_from_c1(request)


def get_links_from_c1(request, serialize=True):
    current_user = request.user
    customer_id = current_user.profile.customer_id
    account_url = 'http://api.reimaginebanking.com/customers/' \
                  '{}/accounts?key={}'.format(customer_id, api_key)
    account_response = requests.get(
        account_url,
        headers={'content-type': 'application/json'},
    ).json()
    links = []
    for account in [x for x in account_response
                    if x['_id'] != current_user.profile.charity_account_id]:
        account_id = account['_id']
        purchases_url = 'http://api.reimaginebanking.com/accounts/{}' \
                        '/purchases?key={}'.format(account_id, api_key)
        purchases_response = requests.get(
            purchases_url,
            headers={'content-type': 'application/json'},
        ).json()

        for purchase in purchases_response:
            try:
                links.append(Link.objects.get(purchase_id=purchase['_id']))
            except Link.DoesNotExist:
                merchant_id = purchase['merchant_id']
                merchant_url = 'http://api.reimaginebanking.com/merchants/{}' \
                               '?key={}'.format(merchant_id, api_key)
                merchant_response = requests.get(
                    merchant_url,
                    headers={'content-type': 'application/json'},
                ).json()
                merchant_category = merchant_response['category']
                merchant_name = merchant_response['name']
                sect = Sector.objects.get(
                    name=sector_map[merchant_category[0]]
                )
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                trans = ""
                purchase_amount = purchase['amount']
                transfer_amount = 0
                try:
                    rule = Rule.objects.get(
                        sector=sect,
                        user=current_user
                    )
                    transfer_amount = purchase_amount * float(rule.rate)
                    payload = {
                        "medium": "balance",
                        "payee_id": str(
                            current_user.profile.charity_account_id
                        ),
                        "amount": purchase_amount * float(rule.rate),
                        "transaction_date": date,
                        "description": "A pledge to charity made to match {}\'s"
                                       " purchase of ${} from {}".format(
                            current_user.username,
                            purchase_amount,
                            merchant_name
                        )
                    }
                    transfer_url = \
                        'http://api.reimaginebanking.com/accounts/{}' \
                        '/transfers?key={}'.format(account_id, api_key)
                    transfer_response = requests.post(
                        transfer_url,
                        data=json.dumps(payload),
                        headers={'content-type': 'application/json'}
                    ).json()
                    trans = transfer_response['objectCreated']['_id']
                except Rule.DoesNotExist:
                    pass

                links.append(Link.objects
                             .create(purchase_id=purchase['_id'],
                                     transfer_id=trans,
                                     sector=sect,
                                     merchant=merchant_name,
                                     date=date,
                                     purchase_amount=purchase_amount,
                                     transfer_amount=transfer_amount))
    if not serialize:
        return links
    serializer = LinkSerializer(links,
                                context={'request': request},
                                many=True)
    return Response(serializer.data)
