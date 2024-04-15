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

from django.db.models import F, ExpressionWrapper, fields
from django.db.models import Sum
from datetime import timedelta


from django.contrib.auth.decorators import login_required
import uuid

@api_view(['POST'])
@permission_classes([AllowAny])
def upload_photo(request):
    if request.method == 'POST':
        photo_data = request.POST.get('photo')
        # user_id = request.POST.get('user_id') or None   # Get the logged-in user ID
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
            print(path)
            # Classify the face detected in the uploaded image
            detected_user = classify_face(path, 0.4)
            
            # Get the logged-in user
            # try:
            #     logged_in_user = UserAccount.objects.get(id=user_id)
            # except UserAccount.DoesNotExist:
            #     return JsonResponse({'error': 'Logged-in user not found'}, status=400)

            # if detected_user == logged_in_user.email:
                # Detected user matches logged-in user
                # Proceed with check-in or check-out process
            if detected_user:
                logged_in_user  =  UserAccount.objects.get(email=detected_user)
                try:
                    if check_type == 'checkin':
                        CheckInAndOut.objects.create(
                            type=check_type,
                            user=logged_in_user,
                            image=path,
                            created_at=check_time
                        )
                        return JsonResponse({'message': f'Check-in successful for user: {logged_in_user.email}'})
                    elif check_type == 'checkout':
                        CheckInAndOut.objects.create(
                            type=check_type,
                            user=logged_in_user,
                            image=path,
                            created_at=check_time
                        )

                        latest_checkin = CheckInAndOut.objects.filter(user=logged_in_user, type='checkin').latest('created_at')
                        latest_checkout = CheckInAndOut.objects.filter(user=logged_in_user, type='checkout').latest('created_at')
                        
                        working_time = latest_checkout.created_at - latest_checkin.created_at

                        # Retrieve the latest break-in and break-out records
                        try:
                            latest_breakin = BreakInAndOut.objects.filter(user=logged_in_user, type='breakin').latest('created_at')
                            latest_breakout = BreakInAndOut.objects.filter(user=logged_in_user, type='breakout').latest('created_at')
                            break_time = latest_breakout.created_at - latest_breakin.created_at
                        except BreakInAndOut.DoesNotExist:
                            # If no break-in and break-out records exist, assume no breaks were taken
                            break_time = timedelta(0)

                        total_working_time = working_time - break_time

                        # Create a new entry in the TimeSheet model
                        TimeSheet.objects.create(
                            user=logged_in_user,
                            date=check_time.date(),
                            working_time=total_working_time,
                            break_time=break_time
                        )
                        return JsonResponse({'message': f'Check-out successful for user: {logged_in_user.email}'})
                    else:
                        return JsonResponse({'error': 'Invalid type provided'}, status=400)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=400)
            else:
                # Detected user does not match logged-in user
                # Return error indicating user not detected
                return JsonResponse({'error': 'User not detected'}, status=400)
        else:
            return JsonResponse({'error': 'No photo found in the request'}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def mark_attendance_without_login(request):
    if request.method == 'POST':
        photo_data = request.POST.get('photo')
        check_time = timezone.now()     
        check_type = request.POST.get('type')  

        if photo_data:
            _, str_img = photo_data.split(';base64,')
            decoded_contentfile = base64.b64decode(str_img)

            unique_filename = timezone.now().strftime("%Y%m%d%H%M%S") + '_' + 'attendance.jpg'
            path = os.path.join('media', unique_filename)
            with open(path, 'wb') as f:
                f.write(decoded_contentfile)
            detected_user_email = classify_face(path, 0.4)

            if detected_user_email: 
                detected_user  =  UserAccount.objects.get(email=detected_user_email)
                try:
                    if check_type == 'checkin':
                        CheckInAndOut.objects.create(
                            type=check_type,
                            user=detected_user,
                            image=path,
                            created_at=check_time
                        )
                        return Response({'message': f'Check-in successful for user: {detected_user.email}'})
                    elif check_type == 'checkout':
                        CheckInAndOut.objects.create(
                            type=check_type,
                            user=detected_user,
                            image=path,
                            created_at=check_time
                        )

                        return Response({'message': f'Check-out successful for user: {detected_user.email}'})
                    else:
                        return Response({'error': 'Invalid type provided'}, status=400)
                except Exception as e:
                    return Response({'error': str(e)}, status=400)
            else:
                return Response({'error': 'User not detected'}, status=400)
        else:
            return Response({'error': 'No photo found in the request'}, status=400)





# @api_view(['POST'])
# @permission_classes([AllowAny])
# def upload_photo(request):
#     if request.method == 'POST':
#         photo_data = request.POST.get('photo')
#         check_time = timezone.now()  # Get the current time
#         check_type = request.POST.get('type')  # Get the type data from the request
#         if photo_data:
#             # Splitting the data to separate the base64 header from the actual encoded image data
#             _, str_img = photo_data.split(';base64,')
#             decoded_contentfile = base64.b64decode(str_img)

#             filename = 'upload.png'  
#             path = os.path.join('media', filename)  
#             with open(path, 'wb') as f:
#                 f.write(decoded_contentfile)

#             # Classify the face detected in the uploaded image
#             detected_user = classify_face(path, 0.4)
#             if detected_user:
#                 # Check if the detected user exists in the database
#                 try:
#                     user = UserAccount.objects.get(email=detected_user)
#                     # Check if it's a check-in or check-out request
#                     if check_type == 'checkin':
#                         CheckInAndOut.objects.create(
#                             type=check_type,
#                             user=user,
#                             image=path,
#                             created_at=check_time
#                         )
#                         return JsonResponse({'message': f'Check-in successful for user: {detected_user}'})
#                     elif check_type == 'checkout':
#                         CheckInAndOut.objects.create(
#                             type=check_type,
#                             user=user,
#                             image=path,
#                             created_at=check_time
#                         )

#                         latest_checkin = CheckInAndOut.objects.filter(user=user, type='checkin').latest('created_at')
#                         latest_checkout = CheckInAndOut.objects.filter(user=user, type='checkout').latest('created_at')
                        
#                         working_time = latest_checkout.created_at - latest_checkin.created_at

#                         print(working_time)

#                         latest_breakin = BreakInAndOut.objects.filter(user = user , type = 'breakin').latest('created_at')
#                         latest_breakout = BreakInAndOut.objects.filter(user = user , type = 'breakout').latest('created_at')

#                         break_time = latest_breakout.created_at - latest_breakin.created_at

#                         print(break_time)

#                         total_working_time = working_time - break_time

#                         print(total_working_time)
#                         # Create a new entry in the TimeSheet model
#                         TimeSheet.objects.create(
#                             user=user,
#                             date=check_time.date(),
#                             working_time=total_working_time,
#                             break_time=break_time
#                         )
#                         return JsonResponse({'message': f'Check-out successful for user: {detected_user}'})
#                     else:
#                         return JsonResponse({'error': 'Invalid type provided'}, status=400)
#                 except UserAccount.DoesNotExist:
#                     return JsonResponse({'error': 'Detected user not found or does not exist'}, status=400)
#             else:
#                 return JsonResponse({'error': 'No face detected in the uploaded photo'}, status=400)
#         else:
#             return JsonResponse({'error': 'No photo found in the request'}, status=400)



@api_view(['POST'])
@permission_classes([AllowAny])
def break_in_out(request):
    if request.method == 'POST':
        photo_data = request.POST.get('photo')
        check_time = timezone.now()
        check_type = request.POST.get('type')
        
        if photo_data:
            _, str_img = photo_data.split(';base64,')
            decoded_contentfile = base64.b64decode(str_img)

            # filename = 'break_image.png'
            # path = os.path.join('media', 'break_images', filename)
            # with open(path, 'wb') as f:
            #     f.write(decoded_contentfile)

            filename = 'upload.png'  
            path = os.path.join('media', filename)  
            with open(path, 'wb') as f:
                f.write(decoded_contentfile)

            detected_user = classify_face(path, 0.4)
            if detected_user:
                try:
                    user = UserAccount.objects.get(email=detected_user)
                    if check_type in ['breakin', 'breakout']:
                        BreakInAndOut.objects.create(
                            type=check_type,
                            user=user,
                            image=path,
                            created_at=check_time
                        )
                        return JsonResponse({'message': f'Break {check_type} successful for user: {detected_user}'})
                    else:
                        return JsonResponse({'error': 'Invalid type provided'}, status=400)
                except UserAccount.DoesNotExist:
                    return JsonResponse({'error': 'Detected user not found or does not exist'}, status=400)
            else:
                return JsonResponse({'error': 'No face detected in the uploaded photo'}, status=400)
        else:
            return JsonResponse({'error': 'No photo found in the request'}, status=400)






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

    # Filter break in and break out data for the current day and the specified user
    break_data = BreakInAndOut.objects.filter(
        user_id=user_id,
        created_at__date=today,
    ).values()

    # Convert UTC time to local time for checkin_data
    for data in checkin_data:
        data['created_at'] = data['created_at'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = data['updated_at'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

    # Convert UTC time to local time for timesheet_data
    for data in timesheet_data:
        data['created_at'] = data['created_at'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = data['updated_at'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

    # Convert UTC time to local time for break_data
    for data in break_data:
        data['created_at'] = data['created_at'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = data['updated_at'].astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

    # Combine the data from all models into a single dictionary
    combined_data = {
        'checkin_data': list(checkin_data),
        'timesheet_data': list(timesheet_data),
        'break_data': list(break_data),
    }

    return JsonResponse(combined_data)


from collections import defaultdict

@api_view(['GET'])
@permission_classes([AllowAny])
def get_attendance_list(request, user_id):
    attendance_list = CheckInAndOut.objects.filter(user_id=user_id)
    serialized_data = {}

    for attendance in attendance_list:
        # Convert created_at to the desired timezone
        created_at_local = timezone.localtime(attendance.created_at)

        date_str = created_at_local.date().strftime('%Y-%m-%d')

        if date_str not in serialized_data:
            serialized_data[date_str] = []

        attendance_data = {
            'id': attendance.id,
            'user': {
                'id': attendance.user.id,
                'emp_id': attendance.user.emp_id,
                'name': attendance.user.get_full_name(),
                'email': attendance.user.email
            },
            'image': attendance.image.url if attendance.image else None,
            'created_at': created_at_local.strftime("%Y-%m-%d %I:%M:%S %p"),
            'updated_at': attendance.updated_at.strftime("%Y-%m-%d %I:%M:%S %p") if attendance.updated_at else None,
            'checkin_time': created_at_local.strftime("%I:%M:%S %p") if attendance.type == 'checkin' else None,
            'checkout_time': created_at_local.strftime("%I:%M:%S %p") if attendance.type == 'checkout' else None,
        }

        if attendance.type == 'checkout':
            # Find the corresponding check-in object
            for data in serialized_data[date_str]:
                if data['checkin_time'] is not None and data['checkout_time'] is None:
                    data['checkout_time'] = created_at_local.strftime("%I:%M:%S %p")
                    break
        else:
            serialized_data[date_str].append(attendance_data)

    return Response(serialized_data)






# @api_view(['GET'])
# def get_timesheet_data(request):
#     user = request.user
#     time_sheet_entries = TimeSheet.objects.filter(user=user)
#     serialized_data = []

#     for entry in time_sheet_entries:
#         # Calculate total working time for the day
#         total_working_time = entry.working_time.total_seconds() if entry.working_time else 0

#         # Calculate total break time for the day
#         total_break_time = entry.break_time.total_seconds() if entry.break_time else 0

#         serialized_entry = {
#             'id': entry.id,
#             'user': {
#                 'id': entry.user.id,
#                 'name': entry.user.get_full_name(),
#                 'email': entry.user.email
#             },
#             'date': entry.date.strftime("%Y-%m-%d"),
#             'check_in': None,  
#             'check_out': None,  
#             'total_working_time': total_working_time,
#             'total_break_time': total_break_time,
#             'net_working_time': total_working_time - total_break_time
#         }
#         serialized_data.append(serialized_entry)

#     return Response(serialized_data)

from django.utils import timezone

from django.db.models import Sum

@api_view(['GET'])
def get_timesheet_data(request, user_id):
    time_sheet_entries = TimeSheet.objects.filter(user__id=user_id)

    serialized_data = []
    for entry in time_sheet_entries:
        check_ins = CheckInAndOut.objects.filter(user__id=user_id, type='checkin', created_at__date=entry.date)
        check_outs = CheckInAndOut.objects.filter(user__id=user_id, type='checkout', created_at__date=entry.date)
        break_ins = BreakInAndOut.objects.filter(user__id=user_id, type='breakin', created_at__date=entry.date)
        break_outs = BreakInAndOut.objects.filter(user__id=user_id, type='breakout', created_at__date=entry.date)

        total_working_time = sum((co.created_at - ci.created_at).total_seconds() for ci, co in zip(check_ins, check_outs))
        total_break_time = sum((bo.created_at - bi.created_at).total_seconds() for bi, bo in zip(break_ins, break_outs))
        
        net_working_time = total_working_time - total_break_time

        serialized_entry = {
            'id': entry.id,
            'user': {
                'id': entry.user.id,
                'name': entry.user.get_full_name(),
                'email': entry.user.email
            },
            'date': entry.date.strftime("%Y-%m-%d"),
            'created_at': timezone.localtime(entry.created_at).strftime("%Y-%m-%d %H:%M:%S"),
            'check_ins': [timezone.localtime(ci.created_at).strftime("%Y-%m-%d %H:%M:%S") for ci in check_ins],
            'check_outs': [timezone.localtime(co.created_at).strftime("%Y-%m-%d %H:%M:%S") for co in check_outs],
            'break_ins': [timezone.localtime(bi.created_at).strftime("%Y-%m-%d %H:%M:%S") for bi in break_ins],
            'break_outs': [timezone.localtime(bo.created_at).strftime("%Y-%m-%d %H:%M:%S") for bo in break_outs],
            'total_working_time': total_working_time,
            'total_break_time': total_break_time,
            'net_working_time': net_working_time
        }
        serialized_data.append(serialized_entry)

    # Return only unique dates
    serialized_data = {entry['date']: entry for entry in serialized_data}.values()

    return Response(serialized_data)



# @api_view(['GET'])
# def get_timesheet_data(request, user_id):
#     time_sheet_entries = TimeSheet.objects.filter(user__id=user_id)

#     serialized_data = []
#     for entry in time_sheet_entries:
#         check_in_entry = CheckInAndOut.objects.filter(user__id=user_id, type='checkin', created_at__date=entry.date).first()
#         check_out_entry = CheckInAndOut.objects.filter(user__id=user_id, type='checkout', created_at__date=entry.date).first()
       
#         total_working_time = entry.working_time.total_seconds() if entry.working_time else 0
#         total_break_time = entry.break_time.total_seconds() if entry.break_time else 0
#         net_working_time = total_working_time - total_break_time

#         serialized_entry = {
#             'id': entry.id,
#             'user': {
#                 'id': entry.user.id,
#                 'name': entry.user.get_full_name(),
#                 'email': entry.user.email
#             },
#             'date': entry.date.strftime("%Y-%m-%d"),
#             'created_at': timezone.localtime(entry.created_at).strftime("%Y-%m-%d %H:%M:%S"),
#             'check_in': timezone.localtime(check_in_entry.created_at).strftime("%Y-%m-%d %H:%M:%S") if check_in_entry else None,
#             'check_out': timezone.localtime(check_out_entry.created_at).strftime("%Y-%m-%d %H:%M:%S") if check_out_entry else None,
#             'total_working_time': total_working_time,
#             'total_break_time': total_break_time,
#             'net_working_time': net_working_time
#         }
#         serialized_data.append(serialized_entry)

#     return Response(serialized_data)



