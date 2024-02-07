from django.urls import path, include
from . import views
from .views import  *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('file_upload_view/', views.file_upload_view, name='file_upload_view'),
    path('get_resumes/',views.get_resumes, name='get_resumes' ),
    path('update_multiple_resumes/',views.update_multiple_resumes,name='update_multiple_resumes'),
    path('update_resume/<int:resume_id>/',views.update_resume, name='update_resume'),
    path('delete_resume/<int:resume_id>/', views.delete_resume , name='delete_resume'),
    path('create_candidate/<int:resume_id>/', views.create_candidate, name='create_candidate'),
    path('update_candidate/<int:candidate_id>/', views.update_candidate, name='update_candidate'),
    path('delete_candidate/<int:candidate_id>/', views.delete_candidate, name='delete_candidate')
   
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
