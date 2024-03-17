from rest_framework import serializers
from .models import elementCustomerServiceModel
from drf_extra_fields.fields import Base64ImageField

class elementCustomerServiceModelSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)
    class Meta:
        model = elementCustomerServiceModel
        fields = '__all__'
        