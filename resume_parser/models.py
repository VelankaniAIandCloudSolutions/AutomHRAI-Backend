from django.db import models
from accounts.models import BaseModel

from django.db.models.signals import post_delete
from django.dispatch import receiver
from candidate_ranking.models import Job



class Resume(BaseModel):
    resume_file_path = models.FileField(upload_to='resumes/')
    name = models.CharField(max_length=100,null =True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    education = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    company_name = models.CharField(max_length=1000, null=True, blank=True)
    college_name = models.CharField(max_length=1000, null=True, blank=True)
    designation = models.CharField(max_length=1000, null=True, blank=True)
    experience = models.TextField(null=True, blank=True)
    total_experience = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name or str(self.id)

@receiver(post_delete, sender=Resume)
def submission_delete(sender, instance, **kwargs):
    instance.resume_file_path.delete(False)


class Candidate(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField(max_length=255,null=True, blank=True)
    phone_number = models.CharField(max_length=13,null=True,blank=True)
    resume = models.ForeignKey(Resume,related_name='candidates',on_delete=models.SET_NULL,null=True,blank=True)
    job = models.ForeignKey(Job,related_name='job',on_delete=models.SET_NULL,null=True,blank=True)


    

        
