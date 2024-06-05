import random
import pandas as pd
import json
from django.core.files.uploadedfile import InMemoryUploadedFile
import datetime
from django.http import JsonResponse
from django.shortcuts import render
# Create your views here.
from datetime import date, datetime

import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *
from . import codeigniter_db_module
from app_settings.models import *
from candidate_ranking.models import *
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime

from facial_recognition.models import *
import os
from django.core.exceptions import ObjectDoesNotExist
from urllib.parse import urlparse
from django.db.models import Q


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh_token")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
def get_user_account(request):
    user = request.user
    serializer = UserAccountSerializer(user)
    return Response({
        'user_account': serializer.data
    })


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

        if data.get('is_active') == 'true':
            is_active = True
        else:
            is_active = False

        if data.get('is_staff') == 'true':
            is_staff = True
        else:
            is_staff = False

        if data.get('is_superuser') == 'true':
            is_superuser = True
        else:
            is_superuser = False

        if data.get('is_supervisor') == 'true':
            is_supervisor = True
        else:
            is_supervisor = False

        if data.get('is_supervisor_admin') == 'true':
            is_supervisor_admin = True
        else:
            is_supervisor_admin = False

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
            is_supervisor=is_supervisor,
            is_supervisor_admin=is_supervisor_admin,
            company=company,
            user_image=user_image,
        )

        return Response({'message': 'UserAccount created successfully', 'user_id': user.id})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def create_or_get_location(request):
    if request.method == 'POST':
        try:
            location_data = request.data.get('location')
            user_company = request.user.company if hasattr(
                request.user, 'company') else None
            location = Location.objects.create(
                name=location_data,  company=user_company)
            serializer = LocationSerializer(location)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_location(request, location_id):
    try:
        location = Location.objects.get(pk=location_id)
        location.delete()
        return Response({'message': 'Location deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Location.DoesNotExist:
        return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['PUT'])
# @permission_classes([AllowAny])
# def update_location(request, location_id):
#     try:
#         location = Location.objects.get(pk=location_id)
#         request_data = request.data.copy()
#         serializer = LocationSerializer(
#             location, data=request_data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     except Location.DoesNotExist:
#         return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_location(request, location_id):
    try:
        location = get_object_or_404(Location, pk=location_id)
        # Assuming request data contains only the 'name' field to update
        # or request.data.get('name') if using DRF
        name = request.data.get('name')
        if name:
            location.name = name
            location.save()
            return JsonResponse({'message': 'Location name updated successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Name field not provided'}, status=400)
    except Location.DoesNotExist:
        return JsonResponse({'error': 'Location not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def create_or_get_category(request):
    if request.method == 'POST':
        try:
            category_data = request.data.get('category')
            category = Category.objects.create(name=category_data)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        print("categories", categories)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        category.delete()
        return Response({'message': 'Location deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Location.DoesNotExist:
        return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        request_data = request.data.copy()

        serializer = CategorySerializer(
            category, data=request_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Location.DoesNotExist:
        return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_user(request, user_id):
    try:
        data = request.data
        print(data)
        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if data.get('is_active') == 'true':
            is_active = True
        else:
            is_active = False

        if data.get('is_staff') == 'true':
            is_staff = True
        else:
            is_staff = False

        if data.get('is_superuser') == 'true':
            is_superuser = True
        else:
            is_superuser = False

        if data.get('is_supervisor') == 'true':
            is_supervisor = True
        else:
            is_supervisor = False

        if data.get('is_supervisor_admin') == 'true':
            is_supervisor_admin = True
        else:
            is_supervisor_admin = False

        user.email = data.get('email', user.email)
        user.password = data.get('password', user.password)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.phone_number = data.get('phone_number', user.phone_number)
        user.emp_id = data.get('emp_id', user.emp_id)
        user.is_active = is_active
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_supervisor = is_supervisor
        user.is_supervisor_admin = is_supervisor_admin

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

        elif data.get('user_image') == 'null':
            # Delete the existing user image
            user.user_image.delete(save=False)

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
@permission_classes([IsAuthenticated])
def check_login(request):
    print(request.user)
    return Response(data={'test': 'test'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_agency(request, agency_id):

    agency = Agency.objects.get(id=agency_id)
    agency.delete()
    return Response({'message': 'Agency deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def agency_list(request):
    if request.method == 'GET':
        agencies = Agency.objects.all()
        serializer = AgencySerializer(agencies, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        name = request.data.get('name')
        agency_owner = request.data.get('ownerName')
        gst = request.data.get('gst')
        labour_license = request.FILES.get('labourLicense')
        pan = request.FILES.get('pan')
        wcp = request.FILES.get('wcp')

        agency = Agency.objects.create(
            name=name,
            agency_owner=agency_owner,
            gst=gst,
            labour_license=labour_license,
            pan=pan,
            wcp=wcp
        )
        serializer = AgencySerializer(agency)

        return Response({'message': 'Agency created successfully', 'data': serializer.data})


@api_view(['DELETE'])
def delete_agency(request, agency_id):

    agency = Agency.objects.get(id=agency_id)
    agency.delete()
    return Response({'message': 'Agency deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
def edit_agency(request, agency_id):
    try:
        print(request.data)
        agency = Agency.objects.get(pk=agency_id)

        agency.name = request.data.get('name', agency.name)
        agency.agency_owner = request.data.get(
            'ownerName', agency.agency_owner)
        agency.gst = request.data.get('gst', agency.gst)

        agency.labour_license = request.FILES.get(
            'labourLicense', agency.labour_license)
        agency.pan = request.FILES.get('pan', agency.pan)
        agency.wcp = request.FILES.get('wcp', agency.wcp)

        clear_labour_license = request.data.get('clearLabourLicense', False)
        clear_pan = request.data.get('clearPan', False)
        clear_wcp = request.data.get('clearWcp', False)
        print(clear_labour_license)
        print(request.FILES.get('labourLicense', agency.labour_license))
        if str(clear_labour_license) == 'true':

            agency.labour_license = None
        else:
            agency.labour_license = request.FILES.get(
                'labourLicense', agency.labour_license)

        if clear_pan == 'true':
            agency.pan = None
        else:
            agency.pan = request.FILES.get('pan', agency.pan)

        if clear_wcp == 'true':
            agency.wcp = None
        else:
            agency.wcp = request.FILES.get('wcp', agency.wcp)

        agency.save()

        serializer = AgencySerializer(agency)

        return Response({'message': 'Agency updated successfully', 'data': serializer.data})
    except Agency.DoesNotExist:
        return Response({'message': 'Agency not found'}, status=404)
    except Exception as e:
        return Response({'message': str(e)}, status=400)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def import_entities_from_automhr(request):
#     entities  = codeigniter_db_module.fetch_all_entities()

#     customer,created = Customer.objects.get_or_create(name='Velankani')
#     company,created = Company.objects.get_or_create(name='Velankani',customer = customer)

#     for entity_data in entities:
#         entity_name = entity_data['branch_name']
#         entity_ref_id = entity_data['branch_id']

#         entity, created = Company.objects.update_or_create(ref_id = entity_ref_id,company =company,defaults={
#             'name': entity_name
#         })

#     return Response({'message':'Entities imported'},status=status.HTTP_200_OK)

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def import_departments_from_automhr(request):
#     departments  = codeigniter_db_module.fetch_all_departments()
#     customer,created = Customer.objects.get_or_create(name='Velankani')
#     company,created = Company.objects.get_or_create(name='Velankani',customer = customer)

#     for department_data in departments:
#         dept_name = department_data['deptname']
#         dept_ref_id = department_data['deptid']
#         entity_ref_id = department_data['branch_id']

#         try:
#             entity = Entity.objects.get(ref_id=entity_ref_id,company = company)
#         except Entity.DoesNotExist:
#             entity = None

#         department, created = Department.objects.update_or_create(name=dept_name,ref_id = dept_ref_id,company =company,defaults={
#             'entity':entity
#         })

#     return Response({'message':'Departments imported'},status=status.HTTP_200_OK)

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def import_jobs_from_automhr(request):
#     jobs  = codeigniter_db_module.fetch_all_jobs()
#     customer,created = Customer.objects.get_or_create(name='Velankani')
#     company,created = Company.objects.get_or_create(name='Velankani',customer = customer)

#     for job_data in jobs:
#         job_name = job_data['job_title']
#         job_ref_id = job_data['id']
#         description = job_data['description']
#         department_id = job_data['department_id']

#         try:
#             department = Department.objects.get(ref_id=department_id,company = company)
#         except Department.DoesNotExist:
#             department = None
#         print(department_id)
#         job, created = Job.objects.update_or_create(name=job_name,ref_id = job_ref_id,company =company,defaults={
#             'job_description':description,
#         })

#         job.departments.add(department)
#         job.save()

#     return Response({'message':'Jobs imported'},status=status.HTTP_200_OK)


@api_view(['GET', 'DELETE'])
@permission_classes([])
def get_and_delete_contract_workers(request, contract_worker_id=None):
    if request.method == 'GET':
        # Retrieve all contract workers
        contract_workers = UserAccount.objects.filter(
            is_contract_worker=True).order_by('-created_at')
        serializer = UserAccountSerializer(contract_workers, many=True)
        data = {"contract_workers": serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        # Delete contract worker by ID
        try:
            if contract_worker_id:
                contract_worker = UserAccount.objects.get(
                    id=contract_worker_id, is_contract_worker=True)
                contract_worker.delete()
                # Define the full URL of the API endpoint
                user_data = {
                    'name': contract_worker.get_full_name(),
                    'email': contract_worker.email,
                }

                delete_url = f'http://localhost:5000/api/v1/delete-contract-worker/{contract_worker_id}'

                # Make a DELETE request to delete the contract worker
                response = requests.delete(delete_url, data=user_data)

                # Check the response status code
                if response.status_code == 204:
                    print('Contract worker  folder deleted from s3 successfully')
                elif response.status_code == 404:
                    print('Error removing contract worker folder from s3,',
                          response.content.decode())

                return Response({"message": "Contract worker deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Contract worker ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        except UserAccount.DoesNotExist:
            return Response({"error": "Contract worker not found"}, status=status.HTTP_404_NOT_FOUND)


def generate_sequential_number():
    # Assuming you have a function to generate unique sequential numbers
    return random.randint(1000, 9999)


@api_view(['GET', 'POST'])
@permission_classes([])
def get_and_create_contract_worker(request):
    if request.method == 'GET':
        agencies = Agency.objects.all()
        sub_categories = SubCategory.objects.all()

        agency_serializer = AgencySerializer(agencies, many=True)
        subcategory_serializer = SubCategorySerializer(
            sub_categories, many=True)
        return Response({
            'agencies': agency_serializer.data,
            'subCategories': subcategory_serializer.data
        })

    elif request.method == 'POST':
        try:
            data = request.data

            agency_id = data.get('agency', None)
            subcategory_id = data.get('subcategory', None)
            agency = get_object_or_404(Agency, id=agency_id)
            if subcategory_id:
                subcategory = get_object_or_404(SubCategory, id=subcategory_id)
            else:
                subcategory = None
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            raw_password = data.get('password')
            emp_id = data.get('emp_id')
            phone_number = data.get('phone_number')

            aadhaar_card = data.get('aadhaar_card')
            pan = data.get('pan')
            dob = data.get('dob')
            # company = data.get('company')
            company = request.user.company
            # Calculate age from date of birth
            if dob:
                dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
                today = date.today()
                age = today.year - dob_date.year - \
                    ((today.month, today.day) < (dob_date.month, dob_date.day))
            else:
                age = None
                dob = None

            print("Calculated age:", age)

            # Create the UserAccount object

            existing_emails = UserAccount.objects.filter(email=email)

            if existing_emails.exists():
                # Generate a sequential number
                sequential_number = generate_sequential_number()
                email = f"{first_name.replace(' ', '').lower()}{sequential_number}@automhr.com"
            user_account = UserAccount.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                emp_id=emp_id,
                phone_number=phone_number,
                aadhaar_card=aadhaar_card,
                pan=pan,
                dob=dob,
                age=age,
                agency=agency,
                sub_category=subcategory,
                is_contract_worker=True,
                company=company
                # Pass any additional fields
            )

            user_account.set_password(raw_password)
            user_account.save()
            # Additional logic if needed
            # Save each user image individually

            # Declare user_images variable with a default value of an empty list
            user_images = []

            # Retrieve uploaded images if available
            user_images = request.FILES.getlist('user_images')
            print('Number of user images received', len(user_images))

            if len(user_images) > 0:
                # Files are uploaded, proceed with processing them
                for image in user_images:
                    UserDocument.objects.create(
                        user=user_account, document=image)

                user_account.user_image = user_images[0]
                user_account.save()  # Save the changes to the user account
            else:
                # No files uploaded, handle accordingly
                print('No user images received')

            # Prepare the files to be uploaded
            image_urls_s3 = [
                document.document.url for document in user_account.user_documents.all()]
            files = [('images', image) for image in user_images]
            image_urls_s3_string = ','.join(image_urls_s3)
            # print('User data/form_data being sent to Flask API:', user_data)
            # for file in files:
            #     print(
            #         f'File being sent: {file[1].name}, size: {file[1].size} bytes')
            user_data = {
                'user_id': user_account.pk,
                'name': user_account.get_full_name(),
                'email': user_account.email,
                'image_urls_s3': image_urls_s3_string
            }
            response = requests.post(settings.FACIAL_RECOGNITION_SERVER_HOST +  'api/v1/create-contract-worker', data=user_data,)
            if response.status_code == 200:
                print("Image and folders upload successful!")
            else:
                print("Error uploading images and creating folder:", response.text)

            # Return a proper response with a status code
            return Response({"message": "UserAccount created successfully"}, status=201)

        except Exception as e:
            print("Error:", e)
            return Response({"message": "Error creating UserAccount"}, status=500)


def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    return base_url


@api_view(['GET', 'PUT'])
@permission_classes([])
def update_contract_worker(request, worker_id):
    try:
        worker = get_object_or_404(UserAccount, id=worker_id)

        if request.method == 'GET':
            worker_serializer = UserAccountSerializer(worker)
            user_documents = UserDocument.objects.filter(user=worker)
            user_documents_serializer = UserDocumentSerializer(
                user_documents, many=True)

            sub_categories = SubCategory.objects.all()
            subCategories_serializer = SubCategorySerializer(
                sub_categories, many=True)

            return Response({
                "worker": worker_serializer.data,
                "user_documents": user_documents_serializer.data,
                "subCategories": subCategories_serializer.data
            })

        elif request.method == 'PUT':

            # Access deleted images sent with FormData

            deleted_images = request.FILES.getlist('deleted_images')

            # Access image objects sent as part of deleted_images
            deleted_image_paths = request.data.getlist('deleted_images')
            print('deleted_image_paths from req', deleted_image_paths)
            data = request.data.copy()

            # Convert agency data to an instance of the Agency model
            if 'agency' in data:
                agency_id = data['agency']
                agency_instance = get_object_or_404(Agency, id=agency_id)
                data['agency'] = agency_instance

            # Convert subcategory data to an instance of the SubCategory model
            if 'sub_category' in data:
                subcategory_id = data['sub_category']
                subcategory_instance = get_object_or_404(
                    SubCategory, id=subcategory_id)
                data['sub_category'] = subcategory_instance

            # Update the fields if provided in the request data
            for field in ['first_name', 'last_name', 'email', 'password', 'emp_id',
                          'phone_number', 'dob', 'agency', 'sub_category', 'aadhaar_card', 'pan']:
                if field in data:
                    setattr(worker, field, data[field])

                if 'email' in data:
                    email = data['email']
                    existing_emails = UserAccount.objects.filter(email=email)
                    if existing_emails.exists():
                        sequential_number = generate_sequential_number()
                        new_email = f"{worker.first_name.replace(' ', '').lower()}{sequential_number}@automhr.com"
                        setattr(worker, 'email', new_email)

            worker.save()

            clear_aadhaar = data.get('clearAadhaar') if str(
                data.get('clearAadhaar')) == 'true' else False
            clear_pan = data.get('clearPan') if str(
                data.get('clearPan')) == 'true' else False

            print('ad', clear_aadhaar)
            print('pan', clear_pan)

            if clear_aadhaar:
                print('ad cleared')
                worker.aadhaar_card = None
            if clear_pan:
                print('pan cleared')
                worker.pan = None

            worker.save()

            if clear_aadhaar:
                if 'aadhaar_card' in request.FILES:
                    worker.aadhaar_card = request.FILES['aadhaar_card']
            if clear_pan:
                if 'pan' in request.FILES:
                    worker.pan = request.FILES['pan']

            worker.save()

            # Handle user images
            user_images = request.FILES.getlist('user_images')
            print('Number of user images received', user_images)

            for idx, file in enumerate(user_images):
                if file.name == "captured_photo.jpg":
                    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
                    file_extension = os.path.splitext(file.name)[1]
                    unique_filename = f"captured_photo_{timestamp}{file_extension}"
                    user_images[idx].name = unique_filename

            # Get deleted images IDs from the frontend
            # deleted_image_ids = json.loads(data.get('deleted_images', '[]'))

            # # Iterate over each deleted image ID
            # for image_id in deleted_image_ids:
            #     try:
            #         # Try to retrieve the UserDocument object with the given ID
            #         image_to_delete = UserDocument.objects.get(pk=image_id)
            #         # Delete the image if it exists
            #         if worker.user_image == image_to_delete.document:
            #             worker.user_image = None
            #             worker.save()

            #         image_to_delete.delete()
            #         print(f"Deleted image with ID {image_id}")
            #     except UserDocument.DoesNotExist:
            #         # Handle the case where the image with the given ID doesn't exist
            #         print(f"Image with ID {image_id} does not exist")

            # Update existing user documents and create new ones if needed

            if deleted_image_paths and len(deleted_image_paths) > 0:
                print('inside delete iamges apth')
                for path in deleted_image_paths:
                    try:
                        # Assuming 'document' is a property of the worker object
                        print('tis is worker', worker)
                        print('worker.user_image = ', worker.user_image)
                        path_url = urlparse(path).path
                        # Remove leading slash from path_url
                        if path_url.startswith('/'):
                            path_url = path_url[1:]
                        print('Path URL:', path_url)

                        if worker.user_image == path_url:
                            worker.user_image = None
                            worker.save()
                        # Process other operations related to the path as needed
                        UserDocument.objects.get(document=path_url).delete()

                        # user_document = UserDocument.objects.get(
                        #     Q(document__icontains=path_url))
                        # print('user_document', user_document)
                    except ObjectDoesNotExist:
                        print(f"Object with path {path_url} does not exist")

            for image_id in user_images:
                # Check if the image already exists in UserDocument model
                existing_document = UserDocument.objects.filter(
                    user=worker, document=image_id).first()
                if not existing_document:
                    # If the image doesn't exist, create a new user document
                    UserDocument.objects.create(user=worker, document=image_id)

            worker.user_image = user_images[0] if user_images else None
            worker.save()

            # Send a request to the Flask API to update images
            image_urls_s3 = [
                document.document.url for document in UserDocument.objects.filter(user=worker)]
            image_urls_s3_string = ','.join(image_urls_s3)

            # Send a request to the Flask API to update images
            user_data = {
                'user_id': worker.pk,
                'name': worker.get_full_name(),
                'email': worker.email,
                'image_urls_s3': image_urls_s3_string
            }
            response = requests.post(
                'http://localhost:5000/api/v1/update-contract-worker', data=user_data,)
            if response.status_code == 200:
                print("Image inside folders updated successful!")
            else:
                print("Error uploading images and creating folder:", response.text)

            # Return a proper response with a status code
            return Response({"message": "UserAccount created successfully"}, status=201)

            return JsonResponse({"message": "Contract worker updated successfully"})

    except Exception as e:
        print("Error:", e)
        return Response({"message": "Error updating contract worker"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST', 'DELETE', 'PUT'])
@permission_classes([])
def get_delete_and_create_projects(request, project_id=None):
    if request.method == 'GET':
        # Retrieve all projects, locations, and categories
        projects = Project.objects.all()
        locations = Location.objects.all()
        categories = Category.objects.all()
        project_serializer = ProjectSerializer(projects, many=True)
        location_serializer = LocationSerializer(locations, many=True)
        category_serializer = CategorySerializer(categories, many=True)
        data = {
            "projects": project_serializer.data,
            "locations": location_serializer.data,
            "categories": category_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Create a new project
        try:
            name = request.data.get('name')
            location_id = request.data.get('location')
            category_id = request.data.get('category')

            # Retrieve location and category objects
            location = Location.objects.get(id=location_id)
            category = Category.objects.get(id=category_id)

            # Create the project
            project = Project.objects.create(
                name=name,
                location=location,
                category=category
            )

            all_projects = Project.objects.all()
            project_serializer = ProjectSerializer(all_projects, many=True)

            return Response({"projects": project_serializer.data}, status=status.HTTP_201_CREATED)
        except Location.DoesNotExist:
            return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        # Delete project by ID
        try:
            if project_id:
                project = Project.objects.get(id=project_id)
                project.delete()
                return Response({"message": "Project deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Project ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PUT':
        if project_id:
            project = Project.objects.get(pk=project_id)

        try:

            name = request.data.get('name')
            location_id = request.data.get('location')
            category_id = request.data.get('category')

            location = Location.objects.get(id=location_id)
            category = Category.objects.get(id=category_id)

            project.name = name
            project.location = location
            project.category = category
            project.save()

            all_projects = Project.objects.all()
            project_serializer = ProjectSerializer(all_projects, many=True)

            return Response({"projects": project_serializer.data}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        except Location.DoesNotExist:
            return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([])
def get_delete_and_create_subcategories(request, subcategory_id=None):
    if request.method == 'GET':
        # Retrieve all subcategories
        categories = Category.objects.all()
        category_serializer = CategorySerializer(categories, many=True)
        subcategories = SubCategory.objects.all()
        subcategory_serializer = SubCategorySerializer(
            subcategories, many=True)
        data = {
            "categories": category_serializer.data,
            "subCategories": subcategory_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Create a new subcategory
        try:
            name = request.data.get('name')
            category_id = request.data.get('categoryId')
            category = Category.objects.get(id=category_id)
            # You may have additional fields to extract from the request data

            # Create the subcategory
            subcategory = SubCategory.objects.create(
                name=name,
                category=category,
                # Pass additional fields as needed
            )

            all_subcategories = SubCategory.objects.all()
            subcategory_serializer = SubCategorySerializer(
                all_subcategories, many=True)

            return Response(subcategory_serializer.data, status=status.HTTP_201_CREATED)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        # Update an existing subcategory
        try:
            name = request.data.get('name')
            category_id = request.data.get('categoryId')
            category = Category.objects.get(id=category_id)
            subcategory = SubCategory.objects.get(id=subcategory_id)
            subcategory.name = name
            subcategory.category = category
            # Update additional fields as needed
            subcategory.save()

            all_subcategories = SubCategory.objects.all()
            subcategory_serializer = SubCategorySerializer(
                all_subcategories, many=True)

            return Response(subcategory_serializer.data, status=status.HTTP_200_OK)
        except SubCategory.DoesNotExist:
            return Response({"error": "Subcategory not found"}, status=status.HTTP_404_NOT_FOUND)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete subcategory by ID
        try:
            if subcategory_id:
                subcategory = SubCategory.objects.get(id=subcategory_id)
                subcategory.delete()
                return Response({"message": "Subcategory deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Subcategory ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        except SubCategory.DoesNotExist:
            return Response({"error": "Subcategory not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def upload_face_recognition_data(request):
    excel_file_path = './media/face_recognition_data_format.xlsx'

    agency_df = pd.read_excel(excel_file_path, sheet_name='Agencies Format')
    for index, row in agency_df.iterrows():
        agency_name = row['Agency Name']
        owner_name = row['Owner Name']
        gst = row['GST No']

        agency, created = Agency.objects.update_or_create(
            name=agency_name,
            agency_owner=owner_name,
            gst=gst
        )
    print(agency_name)

    category_df = pd.read_excel(
        excel_file_path, sheet_name='Sub Categories Format')

    for index, row in category_df.iterrows():
        category_name = row['Category']
        sub_category_name = row['Sub Category']

        category, created = Category.objects.update_or_create(
            name=category_name)
        subcategory, created = SubCategory.objects.update_or_create(
            name=sub_category_name, category=category)

    location_df = pd.read_excel(excel_file_path, sheet_name='Locations Format')

    for index, row in location_df.iterrows():
        location_name = row['Location Name']

        location, created = Location.objects.update_or_create(
            name=location_name)

    project_df = pd.read_excel(excel_file_path, sheet_name='Projects Format')

    for index, row in project_df.iterrows():
        project_name = row['Project Name']
        location_name = row['Location']
        category_name = row['Category']

        category, created = Category.objects.update_or_create(
            name=category_name)
        try:
            location = Location.objects.get(name=location_name)
        except Location.DoesNotExist:
            pass
        project, created = Project.objects.update_or_create(
            name=project_name, location=location, category=category)

    return Response("Data uploaded successfully.")
