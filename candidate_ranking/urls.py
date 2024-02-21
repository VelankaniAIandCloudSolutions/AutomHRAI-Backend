from django.urls import path, include
from . import views
from .views import  *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('department_list/',views.department_list, name='department_list'),
    path('jobgroup_list/', views.jobgroup_list, name='jobgroup_list'),
    path('get_jobs/',views.get_jobs, name='get_jobs'),
    path('create_job_group/<int:department_id>/', views.create_job_group, name='create_job_group'),
    path('update_job_group/<int:job_group_id>/',views.update_job_group, name='update_job_group'),
    path('delete_job_group/<int:job_group_id>/',views.delete_job_group,name='delete_job_group'),
    path('create_job/<int:job_group_id>/', views.create_job,name='create_job'),
    path('update_job/<int:job_id>/', views.update_job, name='update_job'),
    path('delete_job/<int:job_id>/',views.delete_job,name='delete_job'),
    path('rank_candidates/<int:job_id>/',views.rank_candidates,name='rank_candidates'),
    
    
]