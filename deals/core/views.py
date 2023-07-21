import csv

from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum, Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import Customer, Gem, Deal
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
        ).filter(num_customers__gte=2)

        result = []
        for customer in top_customers:
            customer_data = {
                'username': customer.username,
                'spent_money': customer.spent_money,
                'gems': gems_list.filter(
                    deals__customer=customer
                ).values_list('name', flat=True)
            }
            result.append(customer_data)

        cache.set('result', result, 60 * 10)
        return Response({'response': result}, status=status.HTTP_200_OK)

    def create(self, request):
        try:
            file_serializer = self.serializer_class(data=request.data)
            file_serializer.is_valid(raise_exception=True)
            file = file_serializer.validated_data['deals']
            file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(file)

            Deal.objects.all().delete()
            Customer.objects.all().delete()
            Gem.objects.all().delete()

            deals_list = []
            for row in reader:
                serializer = DealSerializer(data=row)
                serializer.is_valid(raise_exception=True)
                customer, _ = Customer.objects.get_or_create(
                    **serializer.validated_data.pop('customer')
                )
                item, _ = Gem.objects.get_or_create(
                    **serializer.validated_data.pop('item')
                )
                deals_list.append(Deal(
                    **serializer.validated_data, customer=customer, item=item)
                )
            Deal.objects.bulk_create(deals_list)
            return Response({'Status': 'OK'}, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response({'Status': 'Error', 'Desc': exc},
                            status=status.HTTP_400_BAD_REQUEST)
