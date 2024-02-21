from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from rest_framework.response import Response

from .utils import classify_face
from accounts.models import UserAccount

# Create your views here.


from django.core.files.base import ContentFile
import base64
import os

from django.utils import timezone

from .models import *
from .serializers import *


from django.http import JsonResponse
from django.utils import timezone
from .models import CheckInAndOut

@api_view(['POST'])
@permission_classes([AllowAny])
def upload_photo(request):
    if request.method == 'POST':
        photo_data = request.POST.get('photo')
        check_time = timezone.now()  # Get the current time
        check_type = request.POST.get('type')  # Get the type data from the request
        if photo_data:
            # Splitting the data to separate the base64 header from the actual encoded image data
            _, str_img = photo_data.split(';base64,')
            decoded_contentfile = base64.b64decode(str_img)

            filename = 'upload.png'  
            path = os.path.join('media', filename)  
            with open(path, 'wb') as f:
                f.write(decoded_contentfile)

            # Classify the face detected in the uploaded image
            detected_user = classify_face(path, 0.4)
            if detected_user:
                # Check if the detected user exists in the database
                try:
                    user = UserAccount.objects.get(email=detected_user)
                    # Check if it's a check-in or check-out request
                    if check_type == 'checkin':
                        CheckInAndOut.objects.create(
                            type=check_type,
                            user=user,
                            image=path,
                            created_at=check_time
                        )
                        return JsonResponse({'message': f'Check-in successful for user: {detected_user}'})
                    elif check_type == 'checkout':
                        CheckInAndOut.objects.create(
                            type=check_type,
                            user=user,
                            image=path,
                            created_at=check_time
                        )

                        latest_checkin = CheckInAndOut.objects.filter(user=user, type='checkin').latest('created_at')
                        latest_checkout = CheckInAndOut.objects.filter(user=user, type='checkout').latest('created_at')
                        # Calculate the working time
                        working_time = latest_checkout.created_at - latest_checkin.created_at
                        # Create a new entry in the TimeSheet model
                        TimeSheet.objects.create(
                            user=user,
                            date=check_time.date(),
                            working_time=working_time
                        )
                        return JsonResponse({'message': f'Check-out successful for user: {detected_user}'})
                    else:
                        return JsonResponse({'error': 'Invalid type provided'}, status=400)
                except UserAccount.DoesNotExist:
                    return JsonResponse({'error': 'Detected user not found or does not exist'}, status=400)
            else:
                return JsonResponse({'error': 'No face detected in the uploaded photo'}, status=400)
        else:
            return JsonResponse({'error': 'No photo found in the request'}, status=400)




# @api_view(['POST'])
# @permission_classes([AllowAny])
# def upload_photo(request):
#     if request.method == 'POST':
#         photo_data = request.POST.get('photo')
#         checkin_time = timezone.now()  # Get the current time
#         type = request.POST.get('type')  # Get the type data from the request
#         if photo_data:
#             # Splitting the data to separate the base64 header from the actual encoded image data
#             _, str_img = photo_data.split(';base64,')
#             decoded_contentfile = base64.b64decode(str_img)

#             filename = 'upload.png'  
#             path = os.path.join('media', filename)  
#             with open(path, 'wb') as f:
#                 f.write(decoded_contentfile)

#             print(path)

#             # Classify the face detected in the uploaded image
#             detected_user = classify_face(path, 0.4)
#             print(detected_user)
#             if detected_user:
#                 # Check if the detected user exists in the database
#                 try:
#                     user = UserAccount.objects.get(email=detected_user)
#                     # Create a CheckInAndOut instance and save it to the database
#                     check_in_out = CheckInAndOut.objects.create(
#                         type=type,  # Set the type field based on the request data
#                         user=user,
#                         image=path,
#                         created_at=checkin_time  # Set the created_at field
#                     )
#                     return JsonResponse({'message': f'Photo received and processed successfully. Detected user: {detected_user}'})
#                 except UserAccount.DoesNotExist:
#                     return JsonResponse({'error': 'Detected user not found or does not exist'}, status=400)
#             else:
#                 return JsonResponse({'error': 'No face detected in the uploaded photo'}, status=400)
#         else:
#             return JsonResponse({'error': 'No photo found in the request'}, status=400)


import pytz

@api_view(['GET'])
@permission_classes([AllowAny])
def get_checkin_data(request, user_id):
    # Get the current date
    today = timezone.now().date()

    # Filter check-in and check-out data for the current day and the specified user
    checkin_data = CheckInAndOut.objects.filter(
        user_id=user_id,
        created_at__date=today,
    ).values()

    # Filter timesheet data for the current day and the specified user
    timesheet_data = TimeSheet.objects.filter(
        user_id=user_id,
        date=today,
    ).values()

    # Convert UTC time to local time for checkin_data
    import pytz

    # Convert UTC time to local time for checkin_data
    for data in checkin_data:
        data['created_at'] = data['created_at'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = data['updated_at'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

    # Convert UTC time to local time for timesheet_data
    for data in timesheet_data:
        data['created_at'] = data['created_at'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = data['updated_at'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')


    # Combine the data from both models into a single dictionary
    combined_data = {
        'checkin_data': list(checkin_data),
        'timesheet_data': list(timesheet_data),
    }

    return Response(combined_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_attendance_list(request):
    attendance_list = CheckInAndOut.objects.all()
    serialized_data = {}
    
    for attendance in attendance_list:
        user_id = attendance.user.id
        if user_id not in serialized_data:
            serialized_data[user_id] = {
                'id': attendance.id,
                'user': {
                    'id': attendance.user.id,
                    'name': attendance.user.get_full_name(),  
                    'email': attendance.user.email
                },
                'image': attendance.image.url if attendance.image else None,
                'created_at': attendance.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'updated_at': attendance.updated_at.strftime("%Y-%m-%d %H:%M:%S") if attendance.updated_at else None,
                'checkin_time': None,
                'checkout_time': None,
            }
        
        if attendance.type == 'checkin':
            serialized_data[user_id]['checkin_time'] = attendance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        elif attendance.type == 'checkout':
            serialized_data[user_id]['checkout_time'] = attendance.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    return Response(list(serialized_data.values()))


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_attendance_list(request):

#     attendace_list = CheckInAndOut.objects.all()

#     serializers = CheckInAndOutSerializer(attendace_list , many = True)

#     return Response(serializers.data)