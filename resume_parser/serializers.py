from rest_framework import serializers
from .models import Resume , Candidate

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'

class CandidateSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer()

    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'resume')