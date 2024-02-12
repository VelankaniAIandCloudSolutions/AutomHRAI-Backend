from django.contrib import admin
from .models import Job, JobGroup, Department


admin.site.register(Department)
admin.site.register(JobGroup)
admin.site.register(Job)


# Register your models here.
