from django.urls import path, include
from . import views
from .views import  *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload-resumes/', views.upload_resumes, name='upload_resumes'),
    path('get_resumes/',views.get_resumes, name='get_resumes' ),
    # path('candidate_list/', views.candidate_list, name='candidate_list'),
    path('update_multiple_resumes/<job_id>/',views.update_multiple_resumes,name='update_multiple_resumes'),
    path('download_resume/<int:resume_id>/', views.download_resume, name='download_resume'),
    path('update_resume/<int:resume_id>/',views.update_resume, name='update_resume'),
    path('delete_resume/<int:resume_id>/', views.delete_resume , name='delete_resume'),
    path('create_candidate/<int:resume_id>/<int:job_id>/', views.create_candidate, name='create_candidate'),
    path('update_candidate/<int:candidate_id>/', views.update_candidate, name='update_candidate'),
    path('delete_candidate/<int:candidate_id>/', views.delete_candidate, name='delete_candidate'),

    path('get_candidate_list/', views.get_candidate_list , name = 'get_candidate_list')
   
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
