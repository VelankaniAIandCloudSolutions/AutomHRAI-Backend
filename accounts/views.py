from django.shortcuts import render
# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from .serializers import UserAccountSerializer, UserCreateSerializer
from .models import UserAccount , Company
from . import codeigniter_db_module
from app_settings.models import *
from candidate_ranking.models import *

@api_view(['GET'])
@permission_classes([])
def get_all_users(request):
    users = UserAccount.objects.all()
    users_serializer = UserAccountSerializer(users, many=True)
    return Response({
        'users': users_serializer.data,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_authenticated_user(request):
    user = request.user 
    serializer = UserAccountSerializer(user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([])
def get_user_by_id(request, user_id):
    user = UserAccount.objects.get(id=user_id)
    user_serializer = UserAccountSerializer(user)

    return Response({
        'user': user_serializer.data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        is_active = data.get('is_active', True)
        is_staff = data.get('is_staff', False)
        is_superuser = data.get('is_superuser', False)
        company_id = data.get('company_id') 
        user_image = request.FILES.get('user_image')
        emp_id = data.get('emp_id')
        company = None
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({'error': 'Invalid company_id'}, status=400)

        user = UserAccount.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            emp_id=emp_id,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            company=company,
            user_image=user_image,
        )

        return Response({'message': 'UserAccount created successfully', 'user_id': user.id})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_user(request, user_id):
    try:
        data = request.data
        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.email = data.get('email', user.email)
        user.password = data.get('password', user.password) 
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.phone_number = data.get('phone_number', user.phone_number)
        user.emp_id = data.get('emp_id', user.emp_id)
        user.is_active = data.get('is_active', user.is_active)
        user.is_staff = data.get('is_staff', user.is_staff)
        user.is_superuser = data.get('is_superuser', user.is_superuser)
        
        company_id = data.get('company_id') 
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                user.company = company
            except Company.DoesNotExist:
                return Response({'error': 'Invalid company_id'}, status=status.HTTP_400_BAD_REQUEST)

        user_image = request.FILES.get('user_image')
        if user_image:
            user.user_image = user_image

        user.save()

        return Response({'message': 'UserAccount updated successfully', 'user_id': user.id})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_user(request, user_id):
    user = get_object_or_404(UserAccount, id=user_id)
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def check_login(request):
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def import_entities_from_automhr(request):
    entities  = codeigniter_db_module.fetch_all_entities()

    customer,created = Customer.objects.get_or_create(name='Velankani')
    company,created = Company.objects.get_or_create(name='Velankani',customer = customer)

    for entity_data in entities:
        entity_name = entity_data['branch_name']
        entity_ref_id = entity_data['branch_id']

        entity, created = Entity.objects.update_or_create(ref_id = entity_ref_id,company =company,defaults={
            'name': entity_name
        })
        
    return Response({'message':'Entities imported'},status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def import_departments_from_automhr(request):
    departments  = codeigniter_db_module.fetch_all_departments()
    customer,created = Customer.objects.get_or_create(name='Velankani')
    company,created = Company.objects.get_or_create(name='Velankani',customer = customer)

    for department_data in departments:
        dept_name = department_data['deptname']
        dept_ref_id = department_data['deptid']
        entity_ref_id = department_data['branch_id']
    
        try:
            entity = Entity.objects.get(ref_id=entity_ref_id,company = company)
        except Entity.DoesNotExist:
            entity = None

        department, created = Department.objects.update_or_create(name=dept_name,ref_id = dept_ref_id,company =company,defaults={
            'entity':entity
        })
        
    return Response({'message':'Departments imported'},status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def import_jobs_from_automhr(request):
    jobs  = codeigniter_db_module.fetch_all_jobs()
    customer,created = Customer.objects.get_or_create(name='Velankani')
    company,created = Company.objects.get_or_create(name='Velankani',customer = customer)

    for job_data in jobs:
        job_name = job_data['job_title']
        job_ref_id = job_data['id']
        description = job_data['description']
        department_id = job_data['department_id']

        try:
            department = Department.objects.get(ref_id=department_id,company = company)
        except Department.DoesNotExist:
            department = None
        print(department_id)
        job, created = Job.objects.update_or_create(name=job_name,ref_id = job_ref_id,company =company,defaults={
            'job_description':description,
        })

        job.departments.add(department)
        job.save()
        
    return Response({'message':'Jobs imported'},status=status.HTTP_200_OK)