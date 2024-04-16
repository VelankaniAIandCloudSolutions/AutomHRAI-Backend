from django.urls import path
from .views import *

urlpatterns = [
    path('upload_photo/', upload_photo, name='upload_photo'),
    path('mark_attendance_without_login/', mark_attendance_without_login, name='mark_attendance_without_login'),
    path('assign_project/', assign_project, name='assign_project'),
    path('get_attendance_list/<int:user_id>', get_attendance_list , name='get_attendance_list'),
    path('get_checkin_data/<int:user_id>/', get_checkin_data , name = 'get_checkin_data'),
    path('break_in_out/' , break_in_out , name = 'break_in_out'),
    path('get_timesheet_data/<int:user_id>/' ,  get_timesheet_data , name = 'get_timesheet_data'),
    path('get_contract_worker_attendance' ,  get_contract_worker_attendance , name = 'get_contract_worker_attendance'),
]