from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.db import IntegrityError
from .models import JobGroup, Department, Job



@api_view(['POST'])
@permission_classes([AllowAny])
def create_job_group(request , department_id):
    
    name = request.data.get('name')
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        return Response({'message': 'Department does not exist'}, status=400)

    job_group = JobGroup.objects.create(name=name, department=department)

    response_data = {
        'message': 'JobGroup created successfully',
        'jobGroup': {
            'id': job_group.id,
            'name': job_group.name,
            'department_id': job_group.department.id if job_group.department else None,
            'isActive': True
        }
    }

    return Response(response_data)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_job_group(request, job_group_id):
    try:
        job_group = JobGroup.objects.get(id=job_group_id)
    except JobGroup.DoesNotExist:
        return Response({'message': 'JobGroup not found'}, status=404)

    name = request.data.get('name')
    department_id = request.data.get('department_id')

    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        return Response({'message': 'Department does not exist'}, status=400)

    job_group.name = name
    job_group.department = department
    job_group.save()

    response_data = {
        'message': 'JobGroup updated successfully',
        'jobGroup': {
            'id': job_group.id,
            'name': job_group.name,
            'department_id': job_group.department.id if job_group.department else None,
            'isActive' : True
        }
    }

    return Response(response_data)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_job_group(request, job_group_id):
    try:
        job_group = JobGroup.objects.get(id=job_group_id)
    except JobGroup.DoesNotExist:
        return Response({'message': 'JobGroup not found'}, status=404)

    job_group.delete()

    return Response({'message': 'JobGroup deleted successfully'}, status=204)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def create_job(request, job_group_id):
    name = request.data.get('name')
    job_description = request.data.get('job_description')
    department_name = request.data.get('department')
    attachment = request.data.get('attachment')

    try:
        job_group = JobGroup.objects.get(pk=job_group_id)
    except JobGroup.DoesNotExist:
        return Response({'error': 'Invalid job_group ID'}, status=400)
    
    try:
        department = Department.objects.get(name=department_name)
    except Department.DoesNotExist:
        return Response({'error': 'Invalid department name'}, status=400)

    job = Job.objects.create(
        name=name,
        job_group=job_group,
        job_description=job_description,
        attachment=attachment,
        department=department,
    )

    return Response({'message': 'Job created successfully', }, status=201)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_job(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'error': 'Invalid job ID'}, status=400)
   

    job.name = request.data.get('name', job.name)
    job.job_description = request.data.get('job_description', job.job_description)
    job.attachment = request.data.get('attachment', job.attachment)
    job.department = request.data.get('department', job.department)
    job.save()

    return Response({'message': 'Job updated successfully'})

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_job(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'error': 'Invalid job ID'}, status=400)

    job.delete()

    return Response({'message': 'Job deleted successfully'})

@api_view(['GET'])
@permission_classes([AllowAny])
def department_list(request):
    departments = Department.objects.all()
    department_list = []

    for department in departments:
        department_list.append({
            'id': department.id,
            'name': department.name,
            'company': department.company.name if department.company else None,
        })

    return Response(department_list)

@api_view(['GET'])
@permission_classes([AllowAny])
def jobgroup_list(request):
    job_groups = JobGroup.objects.all()
    job_group_list = []
    
    for job_group in job_groups:
        job_group_list.append({
            'id': job_group.id,
            'name': job_group.name,
            'department_id': job_group.department.id if job_group.department else None,
            'department_name': job_group.department.name if job_group.department else None,
            'isActive': True
        })
    return Response(job_group_list)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_jobs(request):
    jobs = Job.objects.all()
    job_list = []

    for job in jobs:
        job_list.append({
            'id': job.id,
            'name': job.name,
            'job_group': job.job_group.name if job.job_group else None,
            'job_description': job.job_description,
            'department': job.department.name if job.department else None,
            'attachment': str(job.attachment) if job.attachment else None,
        })

    return Response(job_list)