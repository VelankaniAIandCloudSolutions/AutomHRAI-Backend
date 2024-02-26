from django.db import models
from accounts.models import BaseModel
from app_settings.models import *

class Department(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    entity = models.ForeignKey(Entity, related_name='departments', on_delete=models.SET_NULL, null=True, blank=True)
    ref_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class JobGroup(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.ForeignKey(Department, related_name='job_groups', on_delete=models.SET_NULL, null=True, blank=True)
    ref_id = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name or "Unnamed JobGroup"
    
class Job(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    job_group = models.ForeignKey(JobGroup, related_name='jobs', on_delete=models.SET_NULL, null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)
    departments = models.ManyToManyField(Department, related_name='jobs', blank=True)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    ref_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name or "Unnamed JobGroup"

  
    
    