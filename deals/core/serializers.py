from rest_framework import serializers
from django.core.validators import FileExtensionValidator

from .models import Deal


class FileUploadSerializer(serializers.Serializer):
    deals = serializers.FileField(
        write_only=True,
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
    )

    class Meta:
        fields = ('deals', )


class DealSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source='customer.username')
    item = serializers.CharField(source='item.name')

    class Meta:
        model = Deal
        fields = '__all__'
