from rest_framework.response import Response
from .models import Link
from .serializers import LinkSerializer
from rest_framework.decorators import api_view


@api_view(['GET', 'POST'])
def pull_purchases(request):
    links = Link.objects.all()
    serializer = LinkSerializer(links, many=True)
    return Response(serializer.data)
