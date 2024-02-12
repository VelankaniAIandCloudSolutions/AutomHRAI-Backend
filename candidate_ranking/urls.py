from django.urls import path, include
from . import views
from .views import  *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create_job_group/<int:department_id>/', views.create_job_group, name='create_job_group'),
    path('update_job_group/<int:job_group_id>/',views.update_job_group, name='update_job_group'),
    path('delete_job_group/<int:job_group_id>/',views.delete_job_group,name='delete_job_group'),
    path('create_job/<int:job_group_id>/', views.create_job,name='create_job'),
    path('update_job/<int:job_id>/', views.update_job, name='update_job'),
    path('delete_job/<int:job_id>/',views.delete_job,name='delete_job'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)