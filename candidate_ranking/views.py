from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.db import IntegrityError
from .models import JobGroup, Department, Job
from resume_parser.models import Resume


from operator import index
from pandas._config.config import options
import Cleaner 
import textract as tx
import pandas as pd
import os
import tf_idf
import nltk
nltk.download('punkt')
import Similar

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
    attachment = request.data.get('attachment')

    try:
        job_group = JobGroup.objects.get(id=job_group_id)
    except JobGroup.DoesNotExist:
        return Response({'error': 'Invalid job_group ID'}, status=400)
    
    # if 'attachment' in request.FILES:
    #     attachment_file = request.FILES['attachment']
    # else:
    #     attachment_file = None

    job = Job.objects.create(
        name=name,
        job_group=job_group,
        job_description=job_description,
        attachment=attachment
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






def read_resumes(list_of_resumes, resume_directory):
    placeholder = []
    for res in list_of_resumes:
        temp = []
        temp.append(res)
        text = tx.process(resume_directory+res, encoding='ascii')
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
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'error': 'Invalid job ID'}, status=400)

    single_job_description = [job.name, job.job_description]
    single_job_document = create_single_job_document(single_job_description)
    Jd = get_cleaned_words(single_job_document)

    jd_database = pd.DataFrame(Jd, columns=["Name", "Context", "Cleaned", "Selective", "Selective_Reduced", "TF_Based"])

    # jd_database.to_csv("Job_Data.csv", index=False)

    resumes  = Resume.objects.filter(candidates__job=job)
    document = []
    resume_file_paths = [resume.resume_file_path.path for resume in resumes]

    document = read_resumes(resume_file_paths)

    Doc = get_cleaned_words(document)

    resume_database = pd.DataFrame(Doc, columns=[
        "Name", "Context", "Cleaned", "Selective", "Selective_Reduced", "TF_Based"])

    # Database.to_csv("Resume_Data.csv", index=False)


    resume_database['Scores'] = calculate_scores(resume_database, jd_database)

    Ranked_resumes = resume_database.sort_values(
        by=['Scores'], ascending=False).reset_index(drop=True)

    Ranked_resumes['Rank'] = pd.DataFrame(
        [i for i in range(1, len(Ranked_resumes['Scores'])+1)])

    print(Ranked_resumes)

    return Response({'message': 'Candidates ranked'})