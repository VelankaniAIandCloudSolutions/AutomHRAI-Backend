from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.http import FileResponse


from django.conf import settings
from django.db import IntegrityError
from .models import Resume, Candidate
from .serializers import ResumeSerializer, CandidateSerializer
from candidate_ranking.models import Job
from pyresparser import ResumeParser
import os


def handle_uploaded_file(file):
    # Define the target directory within the media folder
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'test')

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Generate a unique filename (you can modify this logic as needed)
    filename = os.path.join(upload_dir, file.name)
    print('filename', filename)
    # Save the file to the specified path
    with open(filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return filename


@api_view(['POST'])
@permission_classes([AllowAny])
def file_upload_view(request):
    files = request.FILES.getlist('resumes')
    response_data = []
    
    for file in files:
        print(file)
        saved_path = handle_uploaded_file(file)

        parser = ResumeParser(saved_path)  
        data = parser.get_extracted_data()
        print(data)

        resume = Resume(
            name=data.get('name'),
            email=data.get('email'),
            mobile_number=data.get('mobile_number'),
            education=', '.join(data.get('degree')) if data.get('degree') is not None else None,
            company_name=', '.join(data.get('company_names')) if data.get('company_names') is not None else None,
            college_name=data.get('college_name'),
            designation=data.get('designation'),
            total_experience=data.get('total_experience'),
            skills=', '.join(data.get('skills')) if data.get('skills') is not None else None,
            experience=', '.join(data.get('experience')) if data.get('experience') is not None else None,
        )
        resume.save()

        resume_serializer = ResumeSerializer(resume)
        response_data.append({'file_name': file.name, 'saved_path': saved_path, 'status': 'File saved successfully', 'parsed_data': resume_serializer.data})

    return Response({'message': 'Files uploaded successfully', 'resumes': response_data}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def download_resume(request, resume_id):
    try:
        resume = Resume.objects.get(pk=resume_id)
    except ObjectDoesNotExist:
        return Response({'message': 'Resume not found'}, status=status.HTTP_404_NOT_FOUND)

    if resume.resume_file_path:
        try:
            file_path = resume.resume_file_path.path
            
            with open(file_path, 'rb') as resume_file:
                response = FileResponse(resume_file)
                response['Content-Disposition'] = f'attachment; filename="{resume.resume_file_path.name}"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        raise HttpResponse("Resume file not found or not provided")


@api_view(['GET'])
@permission_classes([AllowAny])

def get_resumes(request):
    resumes = Resume.objects.all()
    serializer = ResumeSerializer(resumes, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_resume(request, resume_id):
    try:
        resume = Resume.objects.get(pk=resume_id)
    except Resume.DoesNotExist:
        return Response({'message': 'Resume not found'}, status=status.HTTP_404_NOT_FOUND)

    updated_data = request.data.get('updated_data', {})
    resume.name = updated_data.get('name', resume.name)
    resume.email = updated_data.get('email', resume.email)
    resume.mobile_number = updated_data.get('mobile_number', resume.mobile_number)
    resume.education = updated_data.get('education', resume.education)
    resume.company_name = updated_data.get('company_name', resume.company_name)
    resume.college_name = updated_data.get('college_name', resume.college_name)
    resume.designation = updated_data.get('designation', resume.designation )
    resume.total_experience = updated_data.get('total_experience', resume.total_experience)
    resume.skills = updated_data.get('skills', resume.skills)
    resume.experience = updated_data.get('experience', resume.experience)

    resume.save()

    resume_serializer = ResumeSerializer(resume, data=updated_data, partial=True)

    if resume_serializer.is_valid():
        resume_serializer.save()
        updated_resume_data = resume_serializer.data
        return Response({'message': 'Resume updated successfully', 'updated_resume': updated_resume_data})
    else:
        return Response({'message': 'Invalid data provided for update', 'errors': resume_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])

def update_multiple_resumes(request):
    try:
        updated_resumes = request.data.get('updated_resumes', [])
        
        response_data = []
        
        for updated_data in updated_resumes:
            resume_id = updated_data.get('id')
            try:
                resume = Resume.objects.get(pk=resume_id)
            except Resume.DoesNotExist:
                response_data.append({'resume_id': resume_id, 'message': 'Resume not found'})
                continue
            
            resume.name = updated_data.get('name', resume.name)
            resume.email = updated_data.get('email', resume.email)
            resume.mobile_number = updated_data.get('mobile_number', resume.mobile_number)
            resume.education = updated_data.get('education', resume.education)
            resume.company_name = updated_data.get('company_name', resume.company_name)
            resume.college_name = updated_data.get('college_name', resume.college_name)
            resume.designation = updated_data.get('designation', resume.designation)
            resume.total_experience = updated_data.get('total_experience', resume.total_experience)
            resume.skills = updated_data.get('skills', resume.skills)
            resume.experience = updated_data.get('experience', resume.experience)

            resume.save()

            resume_serializer = ResumeSerializer(resume, data=updated_data, partial=True)

            if resume_serializer.is_valid():
                resume_serializer.save()
                updated_resume_data = resume_serializer.data
                response_data.append({'resume_id': resume_id, 'message': 'Resume updated successfully', 'updated_resume': updated_resume_data})
            else:
                response_data.append({'resume_id': resume_id, 'message': 'Invalid data provided for update', 'errors': resume_serializer.errors})
            
        
        return Response({'message': 'Bulk update completed', 'updated_resumes': response_data})
    except Exception as e:
        return Response({'message': 'Internal Server Error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_resume(request, resume_id):
    try:
        resume = Resume.objects.get(pk=resume_id)
        resume.delete()
        return Response({'message': 'Resume deleted successfully'}, status=204)
    except Resume.DoesNotExist:
        return Response({'message': 'Resume not found'}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_candidate(request, resume_id, job_id):
    try:
        resume = Resume.objects.get(pk=resume_id)

        name_parts = resume.name.split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        job = Job.objects.get(pk=job_id)
        
        Candidate.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=resume.email,
            phone_number=resume.mobile_number,
            resume=resume,
            job=job
        )

        return Response({'message': 'Candidate created successfully'}, status=status.HTTP_201_CREATED)

    except Resume.DoesNotExist:
        return Response({'error': 'Resume not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['PUT'])
@permission_classes([AllowAny])

def update_candidate(request, candidate_id):
    try:
        candidate = Candidate.objects.get(pk=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

    candidate.first_name = request.data.get('first_name', candidate.first_name)
    candidate.last_name = request.data.get('last_name', candidate.last_name)
    candidate.email = request.data.get('email', candidate.email)
    candidate.phone_number = request.data.get('phone_number', candidate.phone_number)
    candidate.save()

    if candidate.resume:
        resume = candidate.resume
        resume.name = f"{candidate.first_name} {candidate.last_name}".strip()
        resume.email = candidate.email
        resume.mobile_number = candidate.phone_number
        resume.education = request.data.get('education', resume.education)
        resume.company_name = request.data.get('company_name', resume.company_name)
        resume.designation = request.data.get('designation', resume.designation)
        resume.experience = request.data.get('experiance', resume.experience)
        resume.total_experience = request.data.get('total_experience', resume.total_experience)
        resume.skills = request.data.get('skills', resume.skills)
        resume.college_name = request.data.get('college_name', resume.college_name)


        resume.save()



    return Response({'message': 'Candidate updated successfully'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([AllowAny])

def delete_candidate(request, candidate_id):
    try:
        candidate = Candidate.objects.get(pk=candidate_id)
    except Candidate.DoesNotExist:
        return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)

    candidate.delete()
    return Response({'message': 'Candidate deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])

def get_candidate_list(request):
    candidates = Candidate.objects.all()
    
    candidate_serializer = CandidateSerializer(candidates , many = True)

    # print(candidate_serializer)

    return Response(candidate_serializer.data)
