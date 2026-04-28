from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Merchant
from .serializers import MerchantSerializer


class MerchantListView(APIView):
    def get(self, request):
        merchants = Merchant.objects.prefetch_related('bank_accounts').all()
        return Response(MerchantSerializer(merchants, many=True).data)