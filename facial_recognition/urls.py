from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('upload_photo/', upload_photo, name='upload_photo'),
    path('get_classify_face_task_result/<str:task_id>',
         views.get_classify_face_task_result),
    path('mark_attendance_without_login/', mark_attendance_without_login,
         name='mark_attendance_without_login'),
    path('assign_project/', assign_project, name='assign_project'),
    path('get_attendance_list/<int:user_id>',
         get_attendance_list, name='get_attendance_list'),
    path('get_checkin_data/<int:user_id>/',
         get_checkin_data, name='get_checkin_data'),
    path('break_in_out/', break_in_out, name='break_in_out'),
    path('get_timesheet_data/<int:user_id>/',
         get_timesheet_data, name='get_timesheet_data'),
    path('get_contract_worker_attendance',  get_contract_worker_attendance,
         name='get_contract_worker_attendance'),
    path('contract-workers/attendance-report/', views.get_attendance_report),
    path('get_contract_worker_timesheet/', get_contract_worker_timesheet,
         name='get_contract_worker_timesheet'),
    path('get-agencies-and-contract-workers/',
         views.get_agencies_and_contract_workers),
    path('calculate-monthly-contract-worker-timesheet-report/',
         views.calculate_monthly_contract_worker_timesheet_report),
    path('parse_excel_for_contract_workers_creation/',
         views.parse_excel_contract_workers_creation),
    path('create-check-in-out/',
         views.create_check_in_out),
    path('calculate-daily-contract-worker-timesheet/',
         views.calculate_daily_contract_worker_timesheet)

]
