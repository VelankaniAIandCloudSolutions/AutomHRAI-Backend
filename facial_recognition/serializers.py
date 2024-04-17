from rest_framework import serializers
from .models import *
from accounts.serializers import *

from django.conf import settings


class CustomUserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'emp_id']


class CheckInAndOutSerializer(serializers.ModelSerializer):
    user = CustomUserAccountSerializer()
    image = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%d/%m/%Y %I:%M %p')
    location = LocationSerializer()
    project = ProjectSerializer()

    class Meta:
        model = CheckInAndOut
        fields = '__all__'

    def get_image(self, obj):
        if (obj.image):
            return settings.WEBSITE_URL + '/' + str(obj.image)
        else:
            return ''

    def get_type(self, obj):
        if (obj.type == 'checkin'):
            return 'Check In'

        elif (obj.type == 'checkout'):
            return 'Check Out'


class BreakInAndOutSerializer(serializers.ModelSerializer):
    user = UserAccountSerializer()
    image = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%d/%m/%Y %I:%M %p')
    location = LocationSerializer()
    type = serializers.SerializerMethodField()
    project = ProjectSerializer()

    class Meta:
        model = BreakInAndOut
        fields = '__all__'

    def get_image(self, obj):
        if (obj.image):
            return settings.WEBSITE_URL + '/' + str(obj.image)
        else:
            return ''

    def get_type(self, obj):
        if (obj.type == 'breakin'):
            return 'Break In'

        elif (obj.type == 'breakout'):
            return 'Break Out'


class TimeSheetSerializer(serializers.ModelSerializer):
    user = UserAccountSerializer()

    class Meta:
        model = TimeSheet
        fields = '__all__'


class CheckBreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = '__all__'

    def to_representation(self, instance):
        if isinstance(instance, CheckInAndOut):
            return CheckInAndOutSerializer(instance).data
        elif isinstance(instance, BreakInAndOut):
            return BreakInAndOutSerializer(instance).data
        return super().to_representation(instance)
