import csv

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import Customer, Deal, Gem
from .serializers import DealSerializer, FileUploadSerializer


class DealView(ViewSet):
    serializer_class = FileUploadSerializer

    def list(self, request):
        cached_data = cache.get('result')
        if cached_data:
            return Response(
                {'response': cached_data}, status=status.HTTP_200_OK
            )

        top_customers = Customer.objects.annotate(
            spent_money=Sum('deals__total')
        ).order_by(
            '-spent_money'
        )[:settings.CUSTOMERS_IN_RESPONSE].prefetch_related('deals')

        gems_list = Gem.objects.filter(
            deals__customer__in=top_customers
        ).annotate(
            num_customers=Count('deals__customer', distinct=True)
        ).filter(num_customers__gte=settings.NUMBER_OF_GEM)

        result = [
            {
                'username': customer.username,
                'spent_money': customer.spent_money,
                'gems': gems_list.filter(
                    deals__customer=customer
                ).values_list('name', flat=True)
            } for customer in top_customers
        ]

        cache.set('result', result, 60 * 10)
        return Response({'response': result}, status=status.HTTP_200_OK)

    def create(self, request):
        file_serializer = self.serializer_class(data=request.data)
        if not file_serializer.is_valid():
            return Response({'Status': 'Error',
                             'Desc': file_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        file = file_serializer.validated_data['deals']
        file = file.read().decode('utf-8').splitlines()
        data = list(csv.DictReader(file))

        serializer = DealSerializer(data=data, many=True)
        if not serializer.is_valid():
            return Response({'Status': 'Error',
                             'Desc': [er for er in serializer.errors if er]},
                            status=status.HTTP_400_BAD_REQUEST)

        deals_list = [
            Deal(
                **{
                    'total': el['total'],
                    'quantity': el['quantity'],
                    'date': el['date'],
                    'customer': Customer.objects.get_or_create(
                        username=el['customer'])[0],
                    'item': Gem.objects.get_or_create(
                        name=el['item'])[0]
                }
            ) for el in serializer.validated_data
        ]

        Deal.objects.all().delete()
        Deal.objects.bulk_create(deals_list)

        return Response({'Status': 'OK'}, status=status.HTTP_201_CREATED)
