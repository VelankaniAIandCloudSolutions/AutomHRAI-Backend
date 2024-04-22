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


class AgencySerializer(serializers.ModelSerializer):
    labour_license = serializers.SerializerMethodField()
    pan = serializers.SerializerMethodField()
    wcp = serializers.SerializerMethodField()

    class Meta:
        model = Agency
        fields = '__all__'

    def get_labour_license(self, obj):
        def clean_url(url): return url.split('?')[0]
        if not obj.labour_license:
            return None
        return clean_url(obj.labour_license.url)

    def get_pan(self, obj):
        def clean_url(url): return url.split('?')[0]
        if not obj.pan:
            return None
        return clean_url(obj.pan.url)

    def get_wcp(self, obj):
        def clean_url(url): return url.split('?')[0]
        if not obj.wcp:
            return None
        return clean_url(obj.wcp.url)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = Location
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = SubCategory
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    location = LocationSerializer()

    class Meta:
        model = Project
        fields = '__all__'


class UserAccountSerializer(serializers.ModelSerializer):
    user_image = serializers.SerializerMethodField()
    aadhaar_card = serializers.SerializerMethodField()
    pan = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    agency = AgencySerializer()
    company = CompanySerializer()

    class Meta:
        model = UserAccount
        fields = '__all__'

    def get_user_image(self, obj):
        def clean_url(url): return url.split('?')[0]
        if not obj.user_image:
            return None
        return clean_url(obj.user_image.url)

    def get_aadhaar_card(self, obj):
        def clean_url(url): return url.split('?')[0]
        if not obj.aadhaar_card:
            return None
        return clean_url(obj.aadhaar_card.url)

    def get_pan(self, obj):
        def clean_url(url): return url.split('?')[0]
        if not obj.pan:
            return None
        return clean_url(obj.pan.url)

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserDocumentSerializer(serializers.ModelSerializer):
    user = UserAccountSerializer()
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = UserDocument
        fields = '__all__'

    def get_document_url(self, obj):
        def clean_url(url): return url.split('?')[0]
        if not obj.document:
            return None
        return clean_url(obj.document.url)
