from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.db import IntegrityError
from .models import JobGroup, Department, Job
from resume_parser.models import Resume
from .serializers import JobGroupSerializer, JobSerializer

from operator import index
from pandas._config.config import options
import candidate_ranking.utils.Cleaner as Cleaner
import candidate_ranking.utils.tf_idf as tf_idf
import candidate_ranking.utils.Similar as Similar
import textract as tx
import pandas as pd
import os

@api_view(['POST'])
@permission_classes([AllowAny])
def create_job_group(request , department_id):
    
    name = request.data.get('name')
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        return Response({'message': 'Department does not exist'}, status=400)

    job_group = JobGroup.objects.create(name=name, department=department)

    serializer = JobGroupSerializer(job_group)

    response_data = {
        'message': 'JobGroup created successfully',
        'jobGroup': serializer.data  
    }

    return Response(response_data)

# @api_view(['PUT'])
# @permission_classes([AllowAny])
# def update_job_group(request, job_group_id):
#     try:
#         job_group = JobGroup.objects.get(id=job_group_id)
#     except JobGroup.DoesNotExist:
#         return Response({'message': 'JobGroup not found'}, status=404)

#     name = request.data.get('name')
#     department_id = request.data.get('department_id')

#     try:
#         department = Department.objects.get(pk=department_id)
#     except Department.DoesNotExist:
#         return Response({'message': 'Department does not exist'}, status=400)

#     job_group.name = name
#     job_group.department = department
#     job_group.save()

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_job_group(request, job_group_id):
    try:
        job_group = JobGroup.objects.get(id=job_group_id)
    except JobGroup.DoesNotExist:
        return Response({'message': 'JobGroup not found'}, status=404)

    name = request.data.get('name')
    department_id = request.data.get('id')
    print(department_id)
    try:
        department = Department.objects.get(pk=department_id)
    except Department.DoesNotExist:
        return Response({'message': 'Department does not exist'}, status=400)

    job_group.name = name
    job_group.department = department
    job_group.save()

    serializer = JobGroupSerializer(job_group)

    response_data = {
        'message': 'JobGroup updated successfully',
        'jobGroup': serializer.data  
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
        
    )
    job.departments.set([department])

    serializer = JobSerializer(job)

    return Response({'message': 'Job created successfully', 'job': serializer.data}, status=201)


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
    department_name = request.data.get('department')
    if department_name:
        try:
            department = Department.objects.get(name=department_name)
        except Department.DoesNotExist:
            return Response({'error': 'Invalid department name'}, status=400)
        job.departments.set([department])
    job.save()
    
    serializer = JobSerializer(job)

    return Response({'message': 'Job updated successfully', 'job': serializer.data}, status=201)



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
            'department': job.job_group.department.name if job.job_group and job.job_group.department else None,
            'attachment': str(job.attachment) if job.attachment else None,
        })

    return Response(job_list)

def read_resumes(list_of_resumes):
    placeholder = []
    for res in list_of_resumes:
        temp = []
        temp.append(str(res.name)) 
        text = tx.process(res.resume_file_path.path, encoding='ascii')
        text = str(text, 'utf-8')
        temp.append(text)
        placeholder.append(temp)
    return placeholder

def get_cleaned_words(document):
    for i in range(len(document)):
        raw = Cleaner.Cleaner(document[i][1])
        document[i].append(" ".join(raw[0]))
        document[i].append(" ".join(raw[1]))
        document[i].append(" ".join(raw[2]))
        sentence = tf_idf.do_tfidf(document[i][3].split(" "))
        document[i].append(sentence)
    return document



def create_single_job_document(single_job_description):
    job_doc = []
    temp = []
    temp.append(single_job_description[0])
    temp.append(single_job_description[1])
    job_doc.append(temp)
    return job_doc

def calculate_scores(resumes, job_description):
    index = 0
    scores = []
    for x in range(resumes.shape[0]):
        score = Similar.match(
            resumes['TF_Based'][x], job_description['TF_Based'][index])
        scores.append(score)
    return scores

@api_view(['POST'])
@permission_classes([AllowAny])
def rank_candidates(request, job_id):
    try:
        job = Job.objects.get(pk=job_id)
    except Job.DoesNotExist:
        return Response({'error': 'Invalid job ID'}, status=400)

    try:
        single_job_description = [job.name, job.job_description]
        single_job_document = create_single_job_document(single_job_description)
        try:
            Jd = get_cleaned_words(single_job_document)
        except Exception as e:
            return Response({'error': 'Add some more information to Job Description'})

        jd_database = pd.DataFrame(Jd, columns=["Name", "Context", "Cleaned", "Selective", "Selective_Reduced", "TF_Based"])

        resumes = Resume.objects.filter(candidates__job=job)
        if len(resumes) == 0:  # Use len() to check the length
            return Response({'error': 'No Candidates for this Job'}, status=400)

        document = read_resumes(resumes)
        try:
            Doc = get_cleaned_words(document)
        except Exception as e:
            return Response({'error': 'Error processing resume documents'})
        
        resume_database = pd.DataFrame(Doc, columns=["Name", "Context", "Cleaned", "Selective", "Selective_Reduced", "TF_Based"])

        resume_database['Scores'] = calculate_scores(resume_database, jd_database)

        Ranked_resumes = resume_database.sort_values(by=['Scores'], ascending=False).reset_index(drop=True)

        Ranked_resumes['Rank'] = pd.DataFrame([i for i in range(1, len(Ranked_resumes['Scores']) + 1)])

        ranked_resumes_data = []
        for i, row in Ranked_resumes.iterrows():
            resume_info = {
                'id': resumes[i].id, 
                'name': row['Name'],
                'email': resumes[i].email, 
                'scores': row['Scores'],
                'rank': row['Rank']
            }
            ranked_resumes_data.append(resume_info)

        return Response({'message': 'Candidates ranked', 'ranked_resumes': ranked_resumes_data})
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)
