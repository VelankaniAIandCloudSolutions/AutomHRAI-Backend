from rest_framework import serializers
from .models import *
from accounts.serializers import UserAccountSerializer

from django.conf import settings

class CheckInAndOutSerializer(serializers.ModelSerializer):
    user = UserAccountSerializer()
    image = serializers.SerializerMethodField()

    class Meta:
        model = CheckInAndOut
        fields = '__all__'

    def get_image(self,obj):
        if(obj.image):
            return settings.WEBSITE_URL + '/media/' + str(obj.image)
        else:
            return ''


class BreakInAndOutSerializer(serializers.ModelSerializer):
    user = UserAccountSerializer()
    image = serializers.SerializerMethodField()
    class Meta:
        model = BreakInAndOut
        fields = '__all__'

class TimeSheetSerializer(serializers.ModelSerializer):
    user = UserAccountSerializer()
   

    class Meta:
        model = TimeSheet
        fields = '__all__'
