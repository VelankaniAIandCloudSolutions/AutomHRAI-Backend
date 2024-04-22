from rest_framework import serializers
from .models import Resume , Candidate
from django.conf import settings

class ResumeSerializer(serializers.ModelSerializer):
    resume_file_path  = serializers.SerializerMethodField()
    class Meta:
        model = Resume
        fields = '__all__'

    def get_resume_file_path(self,obj):
        clean_url = lambda url: url.split('?')[0]
        if obj.resume_file_path:
            return clean_url(obj.resume_file_path.url)
        return None

class CandidateSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer()

    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'resume')