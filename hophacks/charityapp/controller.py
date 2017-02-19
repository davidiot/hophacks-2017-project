from rest_framework.response import Response
from .models import Link, Sector, Rule
from .serializers import LinkSerializer
from rest_framework.decorators import api_view
import datetime
import requests
import json
from django.http import HttpResponse

sector_map = {'Clothing': 'Clothing',
              'Lodging': 'Travel',
              'Food': 'Food',
              'Health': 'Health',
              'Tech': 'Technology'}


@api_view(['GET'])
def pull_purchases(request):
    current_user = request.user
    customer_id = current_user.profile.customer_id
    api_key = '52f69545ffa7fffb30dc369ac3103f7f'
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
                sect = Sector.objects.get(
                    name=sector_map[merchant_category[0]]
                )
                trans = ""
                try:
                    rule = Rule.objects.get(
                        sector=sect,
                        user=current_user
                    )
                    date = datetime.datetime.now().strftime("%Y-%m-%d")
                    purchase_amount = purchase['amount']
                    payload = {
                        "medium": "balance",
                        "payee_id": str(
                            current_user.profile.charity_account_id
                        ),
                        "amount": purchase_amount * float(rule.rate),
                        "transaction_date": date,
                        "description": "A pledge to charity made to match {}\'s"
                                       " purchase of {} from {}".format(
                            current_user.username,
                            purchase_amount,
                            merchant_response['name']
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
                                     sector=sect))

    serializer = LinkSerializer(links,
                                context={'request': request},
                                many=True)
    return Response(serializer.data)
