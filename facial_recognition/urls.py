from django.urls import path
from .views import *

urlpatterns = [
    path('upload_photo/', upload_photo, name='upload_photo'),
    path('get_attendance_list/', get_attendance_list , name='get_attendance_list'),
    path('get_checkin_data/<int:user_id>/', get_checkin_data , name = 'get_checkin_data'),
    path('break_in_out/' , break_in_out , name = 'break_in_out'),
]