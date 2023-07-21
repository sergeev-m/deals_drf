from django.conf import settings
from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from .models import Deal


class FileUploadSerializer(serializers.Serializer):
    deals = serializers.FileField(
        write_only=True,
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
    )

    class Meta:
        fields = ('deals', )


class DealSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(max_length=settings.CUSTOMER_MAX_LENGTH)
    item = serializers.CharField(max_length=settings.GEM_NAME_MAX_LENGTH)

    class Meta:
        model = Deal
        fields = '__all__'
