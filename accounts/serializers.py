from djoser import serializers as djoser_serializers
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from django.conf import settings

User = get_user_model()

class UserCreateSerializer(djoser_serializers.UserCreateSerializer):
    class Meta(djoser_serializers.UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password',
                  'phone_number', 'is_superuser', 'is_staff', 'company', 'created_at', 'updated_at')


class UserAccountSerializer(serializers.ModelSerializer):
    user_image = serializers.SerializerMethodField()
    
    class Meta:
        model = UserAccount
        fields = '__all__'

    def get_user_image(self, obj):
        if(obj.user_image):
            return settings.WEBSITE_URL + obj.user_image.url
        else:
            return ""