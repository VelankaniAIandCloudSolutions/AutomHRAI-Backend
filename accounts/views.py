import datetime
from django.shortcuts import render
# Create your views here.
from datetime import date, datetime

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


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_location(request, location_id):
    try:
        location = Location.objects.get(pk=location_id)
        request_data = request.data.copy()
        request_data.pop('company', None)
        serializer = LocationSerializer(
            location, data=request_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Location.DoesNotExist:
        return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        agency = Agency.objects.get(pk=agency_id)
        
        agency.name = request.data.get('name', agency.name)
        agency.agency_owner = request.data.get('ownerName', agency.agency_owner)
        agency.gst = request.data.get('gst', agency.gst)
        
        agency.labour_license = request.FILES.get('labourLicense', agency.labour_license)
        agency.pan = request.FILES.get('pan', agency.pan)
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
        contract_workers = UserAccount.objects.filter(is_contract_worker=True)
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
                return Response({"message": "Contract worker deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Contract worker ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        except UserAccount.DoesNotExist:
            return Response({"error": "Contract worker not found"}, status=status.HTTP_404_NOT_FOUND)


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

            # Extract agency and location IDs
            agency_id = data.get('agency')
            location_id = data.get('location')
            subcategory_id = data.get('subcategory')
            print(subcategory_id)

            # Retrieve agency and location objects
            agency = get_object_or_404(Agency, id=agency_id)
            subcategory = get_object_or_404(SubCategory, id=subcategory_id)
            # location = get_object_or_404(Location, id=location_id)

            # Extract other fields
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
                is_contract_worker=True
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

            # Return a proper response with a status code
            return Response({"message": "UserAccount created successfully"}, status=201)

        except Exception as e:
            print("Error:", e)
            return Response({"message": "Error creating UserAccount"}, status=500)

from django.core.files.uploadedfile import InMemoryUploadedFile

@api_view(['GET', 'PUT'])
@permission_classes([])
def update_contract_worker(request, worker_id):
    try:
        worker = get_object_or_404(UserAccount, id=worker_id)

        if request.method == 'GET':
            worker_serializer = UserAccountSerializer(worker)
            user_documents = UserDocument.objects.filter(user=worker)
            user_documents_serializer = UserDocumentSerializer(user_documents, many=True)
            return Response({
                "worker": worker_serializer.data,
                "user_documents": user_documents_serializer.data
            })

        elif request.method == 'PUT':
            data = request.data

            # Update the fields if provided in the request data
            for field in ['first_name', 'last_name', 'email', 'password', 'emp_id',
                          'phone_number', 'dob', 'agency', 'aadhaar_card', 'pan']:
                if field in data:
                    setattr(worker, field, data[field])

            worker.save()

            # Delete all existing user documents associated with the worker
            user_documents = UserDocument.objects.filter(user=worker)
            user_documents.delete()

            # Handle user_images
            user_images = request.FILES.getlist('user_images')
            print('Number of user images received', len(user_images))

            if user_images:
                # Save the first image as user_image for the worker
                worker.user_image = user_images[0]

                # Save the rest of the images in UserDocument model
                for image in user_images:
                    UserDocument.objects.create(
                        user=worker, document=image)

                worker.save()

            return Response({"message": "Contract worker updated successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        print("Error:", e)
        return Response({"message": "Error updating contract worker"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['GET', 'POST', 'DELETE','PUT'])
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
