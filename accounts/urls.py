from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from accounts import views

urlpatterns = [
    path('logout/', logout,),
    path('check-login', check_login, name='check_login'),
    path('users/', get_all_users, name='get_all_users'),
    path('users/<int:user_id>/', get_user_by_id, name='get_user_by_id'),
    path('users/create/', create_user, name='create_user'),
    path('users/update/<int:user_id>/', update_user, name='update_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('get-user-account/', get_user_account, name='get_user_account'),
    path('contract-workers/', views.get_and_delete_contract_workers),
    path('contract-workers/delete/<int:contract_worker_id>/',
         get_and_delete_contract_workers),
    path('contract-workers/create/', views.get_and_create_contract_worker),
    path('projects/', views.get_delete_and_create_projects),
    path('projects/delete/<int:project_id>/',
         views.get_delete_and_create_projects),
    path('projects/edit/<int:project_id>/',
         views.get_delete_and_create_projects),

    path('projects/create/', views.get_delete_and_create_projects),
    path('agency_list/', agency_list, name='agency_list'),
    path('delete_agency/<int:agency_id>/', delete_agency, name='delete_agency'),
    path('locations/create/', create_or_get_location,
         name='create_or_get_location'),
    path('locations/delete/<int:location_id>/',
         delete_location, name='delete_location'),
    path('categories/create/', create_or_get_category,
         name='create_or_get_category'),
    path('categories/delete/<int:category_id>/',
         delete_category, name='delete_category'),

    path('locations/update/<int:location_id>/',
         update_location, name='update_location'),
    path('categories/update/<int:category_id>/',
         update_category, name='update_category'),
    path('sub-categories/', views.get_delete_and_create_subcategories),
    path('sub-categories/delete/<int:subcategory_id>/',
         views.get_delete_and_create_subcategories),
    path('sub-categories/edit/<int:subcategory_id>/',
         views.get_delete_and_create_subcategories),

    path('edit_agency/<int:agency_id>/', edit_agency, name='edit_agency'),
    path('contract-workers/update/<int:worker_id>/',
         update_contract_worker, name='update_contract_worker'),
    path('upload_face_recognition_data/', views.upload_face_recognition_data),
    # path('import-entities-from-automhr/', import_entities_from_automhr,name='import_entities_from_automhr'),
    # path('import-departments-from-automhr/', import_departments_from_automhr,name='import_departments_from_automhr'),
    # path('import-jobs-from-automhr/', import_jobs_from_automhr,name='import_jobs_from_automhr'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
