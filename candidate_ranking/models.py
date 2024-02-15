from django.db import models
from accounts.models import BaseModel
from app_settings.models import *


class Department(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    company = models.ForeignKey(Company, related_name='departments', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
    
class JobGroup(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.ForeignKey(Department, related_name='job_groups', on_delete=models.SET_NULL, null=True, blank=True)
    isActive = models.BooleanField(default=True)
    
class Job(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    job_group = models.ForeignKey(JobGroup, related_name='jobs', on_delete=models.SET_NULL, null=True, blank=True)
    job_description = models.CharField(max_length=250, unique=True, null=True, blank=True)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)

    def __str__(self):
        return self.name

  
    
    