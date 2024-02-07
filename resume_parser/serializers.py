from rest_framework import serializers
from .models import Resume , Candidate

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        # fields = (
        #     'id', 'resume', 'name', 'email', 'mobile_number', 'education',
        #     'skills', 'company_name', 'college_name', 'designation',
        #     'experience', 'uploaded_on', 'total_experience', 'get_resume',
        # )
class CandidateSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer()

    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'resume')