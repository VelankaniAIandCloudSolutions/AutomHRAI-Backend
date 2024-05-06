from django.db.models import Q
from collections import defaultdict
import pandas as pd
import pytz
from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from rest_framework.response import Response

from .utils import classify_face
from accounts.models import UserAccount
from celery.result import AsyncResult
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
from datetime import datetime, timedelta
from django.utils import timezone

from rest_framework import status
from django.contrib.auth.decorators import login_required
import uuid
import json
import base64
import os
from .tasks import *
from django.core.cache import cache
from automhrai.utils import upload_file_to_s3
from django.conf import settings
import calendar
from django.db.models import Count
import datetime


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_photo(request):
    if request.method == 'POST':
        photo_data = request.POST.get('photo')
        # user_id = request.POST.get('user_id') or None   # Get the logged-in user ID
        check_time = timezone.now()  # Get the current time
        # Get the type data from the request
        check_type = request.POST.get('type')

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
                logged_in_user = UserAccount.objects.get(email=detected_user)
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

                        latest_checkin = CheckInAndOut.objects.filter(
                            user=logged_in_user, type='checkin').latest('created_at')
                        latest_checkout = CheckInAndOut.objects.filter(
                            user=logged_in_user, type='checkout').latest('created_at')

                        working_time = latest_checkout.created_at - latest_checkin.created_at

                        # Retrieve the latest break-in and break-out records
                        try:
                            latest_breakin = BreakInAndOut.objects.filter(
                                user=logged_in_user, type='breakin').latest('created_at')
                            latest_breakout = BreakInAndOut.objects.filter(
                                user=logged_in_user, type='breakout').latest('created_at')
                            break_time = latest_breakout.created_at - latest_breakin.created_at
                        except BreakInAndOut.DoesNotExist:
                            # If no break-in and break-out records exist, assume no breaks were taken
                            break_time = datetime.timedelta(0)

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
        data['created_at'] = data['created_at'].astimezone(
            pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = data['updated_at'].astimezone(
            pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

    # Convert UTC time to local time for timesheet_data
    for data in timesheet_data:
        data['created_at'] = data['created_at'].astimezone(
            pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = data['updated_at'].astimezone(
            pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

    # Convert UTC time to local time for break_data
    for data in break_data:
        data['created_at'] = data['created_at'].astimezone(
            pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = data['updated_at'].astimezone(
            pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

    # Combine the data from all models into a single dictionary
    combined_data = {
        'checkin_data': list(checkin_data),
        'timesheet_data': list(timesheet_data),
        'break_data': list(break_data),
    }

    return JsonResponse(combined_data)


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
            'image': attendance.image if attendance.image else None,
            'created_at': created_at_local.strftime("%Y-%m-%d %I:%M:%S %p"),
            'updated_at': attendance.updated_at.strftime("%Y-%m-%d %I:%M:%S %p") if attendance.updated_at else None,
            'checkin_time': created_at_local.strftime("%I:%M:%S %p") if attendance.type == 'checkin' else None,
            'checkout_time': created_at_local.strftime("%I:%M:%S %p") if attendance.type == 'checkout' else None,
        }

        if attendance.type == 'checkout':
            # Find the corresponding check-in object
            for data in serialized_data[date_str]:
                if data['checkin_time'] is not None and data['checkout_time'] is None:
                    data['checkout_time'] = created_at_local.strftime(
                        "%I:%M:%S %p")
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


@api_view(['GET'])
def get_timesheet_data(request, user_id):
    time_sheet_entries = TimeSheet.objects.filter(user__id=user_id)

    serialized_data = []
    for entry in time_sheet_entries:
        check_ins = CheckInAndOut.objects.filter(
            user__id=user_id, type='checkin', created_at__date=entry.date)
        check_outs = CheckInAndOut.objects.filter(
            user__id=user_id, type='checkout', created_at__date=entry.date)
        break_ins = BreakInAndOut.objects.filter(
            user__id=user_id, type='breakin', created_at__date=entry.date)
        break_outs = BreakInAndOut.objects.filter(
            user__id=user_id, type='breakout', created_at__date=entry.date)

        total_working_time = sum((co.created_at - ci.created_at).total_seconds()
                                 for ci, co in zip(check_ins, check_outs))
        total_break_time = sum((bo.created_at - bi.created_at).total_seconds()
                               for bi, bo in zip(break_ins, break_outs))

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

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def mark_attendance_without_login(request):
#     if request.method == 'POST':
#         photo_data = request.POST.get('photo')
#         check_time = timezone.now()
#         check_type = request.POST.get('type')
#         if request.user.location:
#             location = request.user.location
#         else:
#             location = None
#         if photo_data:
#             _, str_img = photo_data.split(';base64,')
#             decoded_contentfile = base64.b64decode(str_img)

#             unique_filename = timezone.now().strftime(
#                 "%Y%m%d%H%M%S") + '_' + 'attendance.jpg'
#             path = os.path.join('media', unique_filename)
#             with open(path, 'wb') as f:
#                 f.write(decoded_contentfile)
#             detected_user_email = classify_face(path, 0.4)

#             if detected_user_email:
#                 print(detected_user_email)
#                 try:
#                     detected_user = UserAccount.objects.get(
#                         email=detected_user_email)
#                     try:
#                         if detected_user.last_name:
#                             full_name = f"{detected_user.first_name} {detected_user.last_name}"
#                         else:
#                             full_name = detected_user.first_name

#                         if check_type == 'checkin':
#                             CheckInAndOut.objects.create(
#                                 type=check_type,
#                                 user=detected_user,
#                                 image=path,
#                                 created_at=check_time,
#                                 location=location
#                             )
#                             return Response({'message': f'Check-in successful for user: {full_name}'})
#                         elif check_type == 'checkout':
#                             CheckInAndOut.objects.create(
#                                 type=check_type,
#                                 user=detected_user,
#                                 image=path,
#                                 created_at=check_time,
#                                 location=location
#                             )
#                             return Response({'message': f'Check-out successful for user: {full_name}'})
#                         elif check_type == 'breakin':
#                             BreakInAndOut.objects.create(
#                                 type=check_type,
#                                 user=detected_user,
#                                 image=path,
#                                 created_at=check_time,
#                                 location=location
#                             )
#                             return Response({'message': f'Break-in successful for user: {full_name}'})
#                         elif check_type == 'breakout':
#                             BreakInAndOut.objects.create(
#                                 type=check_type,
#                                 user=detected_user,
#                                 image=path,
#                                 created_at=check_time,
#                                 location=location
#                             )
#                             return Response({'message': f'Break-out successful for user: {full_name}'})
#                         else:
#                             return Response({'error': 'Invalid type provided'}, status=400)
#                     except Exception as e:
#                         return Response({'error': str(e)}, status=400)
#                 except UserAccount.DoesNotExist:
#                     return Response({'message': 'User not found'}, status=404)
#             else:
#                 return Response({'error': 'User not detected'}, status=400)
#         else:
#             return Response({'error': 'No photo found in the request'}, status=400)

@api_view(['POST'])
def mark_attendance_without_login(request):
    if request.method == 'POST':
        photo_data = request.POST.get('photo')
        check_time = timezone.now()
        check_type = request.POST.get('type')
        location_id = request.user.location.id if request.user.location else None
        if photo_data:
            _, str_img = photo_data.split(';base64,')
            decoded_contentfile = base64.b64decode(str_img)

            unique_filename = timezone.now().strftime(
                "%Y%m%d%H%M%S") + '_' + 'attendance.jpg'
            img_path = os.path.join('media', unique_filename)
            with open(img_path, 'wb') as f:
                f.write(decoded_contentfile)

            cache_key = f"attendance_data_{unique_filename}"
            cache.set(cache_key, {
                      'type': check_type, 'location_id': location_id, 'img_path': img_path}, timeout=600)
            task = async_classify_face.delay(img_path, 0.4)
            return Response({'task_id': task.id, 'status': 'Processing', 'cache_key': cache_key})

        else:
            return Response({'error': 'No photo found in the request'}, status=400)


def handle_attendance_record(user, image_path, check_type, check_time, location):
    current_date = timezone.now().date()

    has_checkin_today = CheckInAndOut.objects.filter(
        Q(user=user, type='checkin', created_at__date=current_date)
    ).exists()
    has_checkout_today = CheckInAndOut.objects.filter(
        Q(user=user, type='checkout', created_at__date=current_date)
    ).exists()

    has_breakin_today = BreakInAndOut.objects.filter(
        Q(user=user, type='breakin', created_at__date=current_date)
    ).exists()
    has_breakout_today = BreakInAndOut.objects.filter(
        Q(user=user, type='breakout', created_at__date=current_date)
    ).exists()

    if check_type == 'checkin':
        if has_checkin_today and not has_checkout_today:
            return None, False, 'User already checked in on the current day'
    elif check_type == 'checkout':
        if not has_checkin_today:
            return None, False, 'User cannot check out without checking in today'
    elif check_type == 'breakin':
        if not has_checkin_today or (has_breakin_today and not has_breakout_today):
            return None, False, 'User cannot break in without checking in or breaking out'
    elif check_type == 'breakout':
        if not has_checkin_today or not has_breakin_today:
            return None, False, 'User cannot break out without checking in or breaking in'
    else:
        return None, False, ''

    if check_type in ['checkin', 'checkout']:
        event, created = CheckInAndOut.objects.update_or_create(
            user=user,
            image=image_path,
            defaults={
                'type': check_type,
                'created_at': check_time,
                'location': location
            }
        )
    elif check_type in ['breakin', 'breakout']:
        event, created = BreakInAndOut.objects.update_or_create(
            user=user,
            image=image_path,
            defaults={
                'type': check_type,
                'created_at': check_time,
                'location': location
            }
        )
    else:
        return None, False, ''

    return event, created, ''


@api_view(['GET'])
def get_classify_face_task_result(request, task_id):
    task_result = AsyncResult(task_id)

    if task_result.ready():
        detected_user_email, attendance_data = task_result.result
        print(detected_user_email)
        if detected_user_email == "Unknown" or detected_user_email is None:
            return Response({'message': 'User not detected', 'status': 'FAILURE'})

        try:
            print('user found', detected_user_email)
            detected_user = UserAccount.objects.get(email=detected_user_email)
            location = Location.objects.get(
                id=attendance_data['location_id']) if attendance_data['location_id'] else None

            s3_object_key = f"attendance_images/{os.path.basename(attendance_data['img_path'])}"
            s3_url = upload_file_to_s3(
                attendance_data['img_path'], settings.AWS_STORAGE_BUCKET_NAME, s3_object_key)
            if s3_url:
                os.remove(attendance_data['img_path'])

                event, created, message = handle_attendance_record(
                    user=detected_user,
                    image_path=s3_url,
                    check_type=attendance_data['type'],
                    check_time=timezone.now(),
                    location=location
                )
                print('message', message)
                if created:
                    return Response({'message': f"{attendance_data['type'].title()} successful for user: {detected_user.get_full_name()}", "status": "SUCCESS"})
                else:
                    return Response({'message': 'Failed to update attendance record, ' + message, 'status': 'FAILURE'})
            else:
                return Response({'message': 'Failed to upload image to S3', 'status': 'FAILURE'}, status=500)
        except UserAccount.DoesNotExist:
            return Response({'message': 'User not found', 'status': 'FAILURE'})
    else:
        return Response({'status': 'PROCESSING'})


@api_view(['POST'])
def get_contract_worker_attendance(request):
    contract_workers = UserAccount.objects.filter(is_contract_worker=True)

    all_entries = []
    if request.data.get('date'):
        selected_date = request.data.get('date')

    else:
        selected_date = datetime.date.today()

    for user in contract_workers:
        user_check_ins = CheckInAndOut.objects.filter(
            user=user, created_at__date=selected_date)
        user_break_ins = BreakInAndOut.objects.filter(
            user=user, created_at__date=selected_date)

        user_entries = list(user_check_ins) + list(user_break_ins)

        all_entries.extend(user_entries)
        
    all_entries.sort(key=lambda entry: entry.created_at, reverse=True)
    entry_serializer = CheckBreakSerializer(all_entries, many=True)
    projects = Project.objects.all()
    projects_serializer = ProjectSerializer(projects, many=True)
    return Response({'checks_breaks': entry_serializer.data, 'projects': projects_serializer.data})


@api_view(['POST'])
def assign_project(request):
    if request.method == 'POST':
        project_id = request.data.get('project_id')
        attendance_entries = json.loads(
            request.data.get('selected_attendance_entries'))

        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not attendance_entries or not isinstance(attendance_entries, list):
            return Response({'error': 'Selected attendance entries data is missing or invalid'}, status=status.HTTP_400_BAD_REQUEST)
        check_in_outs = []
        break_in_outs = []

        try:
            for item in attendance_entries:
                if item['type'] == 'Check In' or item['type'] == 'Check Out':
                    check_in_outs.append(item)
                elif item['type'] == 'Break In' or item['type'] == 'Break Out':
                    break_in_outs.append(item)

            for item in check_in_outs:
                check_in_out = CheckInAndOut.objects.get(id=item['id'])
                check_in_out.project = Project.objects.get(id=project_id)
                check_in_out.save()

            for item in break_in_outs:
                break_in_out = BreakInAndOut.objects.get(id=item['id'])
                break_in_out.project = Project.objects.get(id=project_id)
                break_in_out.save()

            return Response({'message': 'Project assigned successfully'}, status=status.HTTP_200_OK)
        except CheckInAndOut.DoesNotExist:
            return Response({'error': 'One or more check in/out entries not found'}, status=status.HTTP_404_NOT_FOUND)
        except BreakInAndOut.DoesNotExist:
            return Response({'error': 'One or more break in/out entries not found'}, status=status.HTTP_404_NOT_FOUND)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_contract_worker(request):
    contract_workers = UserAccount.objects.filter(is_contract_worker=True)
    serializer = UserAccountSerializer(contract_workers, many=True)

    return Response({'user_data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_attendance_report(request):
    if request.method == 'GET':
        date_str = request.query_params.get('date')

        if not date_str:
            return Response({'error': 'Date is not provided but is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            print(date)
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        contract_workers = UserAccount.objects.filter(is_contract_worker=True)

        response_data = []

        for user in contract_workers:
            user_serializer = UserAccountSerializer(user)

            user_data = {
                'user': user_serializer.data,
                'work_time': None,
                'break_time': None,
                'entries': []
            }

            checkins = CheckInAndOut.objects.filter(
                user=user,
                type='checkin',
                created_at__date=date
            ).order_by('created_at')

            print(checkins)

            checkouts = CheckInAndOut.objects.filter(
                user=user,
                type='checkout',
                created_at__date=date
            ).order_by('created_at')

            breakins = BreakInAndOut.objects.filter(
                user=user,
                type='breakin',
                created_at__date=date
            ).order_by('created_at')

            breakouts = BreakInAndOut.objects.filter(
                user=user,
                type='breakout',
                created_at__date=date
            ).order_by('created_at')

            if checkins.count() != checkouts.count():
                print('not eqs')
                user_data['work_time'] = 'Incomplete check-in/check-out data'
                entries = list(checkins) + list(checkouts) + \
                    list(breakins) + list(breakouts)
                sorted_entries = sorted(
                    entries, key=lambda entry: entry.created_at)
                user_data['entries'] = CheckBreakSerializer(
                    sorted_entries, many=True).data

            else:
                working_hours = sum(
                    (checkout.created_at - checkin.created_at).total_seconds()
                    for checkin, checkout in zip(checkins, checkouts)
                )

                if breakins.count() != breakouts.count():
                    user_data['break_time'] = 'Incomplete break-in/break-out data'
                    entries = list(checkins) + list(checkouts) + \
                        list(breakins) + list(breakouts)
                    sorted_entries = sorted(
                        entries, key=lambda entry: entry.created_at)
                    user_data['entries'] = CheckBreakSerializer(
                        sorted_entries, many=True).data
                else:
                    break_hours = sum(
                        (breakout.created_at - breakin.created_at).total_seconds()
                        for breakin, breakout in zip(breakins, breakouts)
                    )

                    effective_working_hours = max(
                        working_hours - break_hours, 0)
                    user_data['work_time'] = effective_working_hours
                    user_data['break_time'] = break_hours

            # Get all entries
                entries = list(checkins) + list(checkouts) + \
                    list(breakins) + list(breakouts)

                print('entries queryset', entries)

                sorted_entries = sorted(
                    entries, key=lambda entry: entry.created_at)

                print('this is sorted-entries query set', sorted_entries)

                user_data['entries'] = CheckBreakSerializer(
                    sorted_entries, many=True).data

            response_data.append(user_data)

        return Response({'user_data': response_data}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def get_contract_worker_timesheet(request):
    if request.method == 'GET':
        contract_workers = UserAccount.objects.filter(is_contract_worker=True)
        serializer = UserAccountSerializer(contract_workers, many=True)

        return Response({'user_data': serializer.data}, status=status.HTTP_200_OK)

    if request.method == 'POST':
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'error': 'No user ID provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserAccount.objects.get(id=user_id)
        except UserAccount.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')

        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if not start_date:
            checkins = CheckInAndOut.objects.filter(
                user=user_id, type='checkin')
            if checkins.exists():
                earliest_checkin = checkins.order_by(
                    'created_at').first().created_at
                start_date = earliest_checkin.date()  # Extract the date part
            else:
                return Response({'error': 'No checkin entries found'}, status=status.HTTP_400_BAD_REQUEST)

        if not end_date:
            end_date = datetime.now().date()

        date_array = generate_date_array(start_date, end_date)

        time_sheets = []
        for date in date_array:
            work_time, break_time, entries = calculate_timesheet_for_date(
                user, date)
            user_data = {
                'user_info': user.id,
                'date': date,
                'work_time': work_time,
                'break_time': break_time,
                'entries': entries
            }
            time_sheets.append(user_data)

        return Response({'user_data': time_sheets}, status=status.HTTP_200_OK)


def generate_date_array(start_date, end_date):
    date_array = []
    current_date = start_date
    while current_date <= end_date:
        date_array.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    return date_array


def calculate_timesheet_for_date(user, date):
    checkins = CheckInAndOut.objects.filter(
        user=user, type='checkin', created_at__date=date).order_by('created_at')
    checkouts = CheckInAndOut.objects.filter(
        user=user, type='checkout', created_at__date=date).order_by('created_at')
    breakins = BreakInAndOut.objects.filter(
        user=user, type='breakin', created_at__date=date).order_by('created_at')
    breakouts = BreakInAndOut.objects.filter(
        user=user, type='breakout', created_at__date=date).order_by('created_at')
    work_time = calculate_work_time(checkins, checkouts, breakins, breakouts)
    break_time = calculate_break_time(breakins, breakouts, checkins, checkouts)
    entries = serialize_entries(checkins, checkouts, breakins, breakouts)

    return work_time, break_time, entries


def calculate_work_time(checkins, checkouts, breakins, breakouts):
    if checkins.count() != checkouts.count():
        return 'NA'

    working_hours = sum((checkout.created_at - checkin.created_at).total_seconds()
                        for checkin, checkout in zip(checkins, checkouts))
    return working_hours


def calculate_break_time(breakins, breakouts, checkins, checkouts):
    if breakins.count() != breakouts.count():
        return 'NA'

    break_hours = sum((breakout.created_at - breakin.created_at).total_seconds()
                      for breakin, breakout in zip(breakins, breakouts))
    return break_hours


def serialize_entries(checkins, checkouts, breakins, breakouts):
    entries = list(checkins) + list(checkouts) + \
        list(breakins) + list(breakouts)
    sorted_entries = sorted(entries, key=lambda entry: entry.created_at)
    return CheckBreakSerializer(sorted_entries, many=True).data


@api_view(['GET'])
def get_agencies_and_contract_workers(request):
    try:
        if request.method == 'GET':
            agencies = Agency.objects.all()
            agency_serializer = AgencySerializer(agencies, many=True)

            contract_workers = UserAccount.objects.filter(
                is_contract_worker=True)
            contract_worker_serializer = UserAccountSerializer(
                contract_workers, many=True)

            return Response({'agencies': agency_serializer.data, 'contract_workers': contract_worker_serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# def calculate_monthly_contract_worker_timesheet_report(request):
#     try:
#         # Extract formData from request

#         # Extract data from formData
#         agency_id = request.data.get("agency")

#         month = request.data.get("month")
#         print(month)
#         year = request.data.get("year")
#         print(year)

#         # Assuming worker IDs are sent as a list
#         worker_ids = request.data.get("workers")
#         print(worker_ids)

#         if year is None or month is None:
#             return Response({"error": "Year or month is missing from the request."}, status=400)

#         # Convert month to its equivalent integer representation
#         month_dict = {
#             "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
#             "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
#             "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
#         }
#         month_int = month_dict.get(month)

#         if month_int is None:
#             return Response({"error": "Invalid month provided."}, status=400)

#         # Convert year to integer if it's a valid integer
#         try:
#             year_int = int(year)
#         except ValueError:
#             return Response({"error": "Year must be a valid integer."}, status=400)

#         # Get workers based on the provided IDs and conditions
#         if agency_id and worker_ids:  # Condition 1: Both agency and worker IDs provided
#             workers = UserAccount.objects.filter(
#                 id__in=worker_ids, agency_id=agency_id, is_contract_worker=True)
#         elif agency_id:  # Condition 2: Only agency ID provided
#             workers = UserAccount.objects.filter(
#                 agency_id=agency_id, is_contract_worker=True)
#         elif worker_ids:  # Condition 3: Only worker IDs provided
#             workers = UserAccount.objects.filter(
#                 id__in=worker_ids, is_contract_worker=True)
#         else:
#             # No agency or worker IDs provided
#             workers = UserAccount.objects.filter(
#                 is_contract_worker=True)

#         # Dictionary to store timesheet data
#         timesheet_data = {}

#         # Iterate through each worker
#         for worker in workers:
#             timesheet_data[f"{worker.first_name} {worker.last_name}"] = {}
#             # Fetch agency and subcategory details for the current worker
#             agency_name = worker.agency.name if worker.agency else None
#             subcategory_name = worker.sub_category.name if worker.sub_category else None
#             # Iterate through each day of the selected month
#             for day in range(1, 32):
#                 try:
#                     # Get the date of the current day in the loop
#                     current_date = datetime(int(year), month_int, day)
#                     print(current_date)

#                     # Get check-ins and check-outs for the current day
#                     check_ins = CheckInAndOut.objects.filter(
#                         user=worker, type='checkin', created_at__date=current_date)
#                     check_outs = CheckInAndOut.objects.filter(
#                         user=worker, type='checkout', created_at__date=current_date)

#                     # Calculate total effective working time for the current day
#                     effective_working_time = calculate_effective_working_time(
#                         check_ins, check_outs)

#                     # Calculate total break time for the current day
#                     total_break_time = calculate_total_break_time(
#                         check_ins, check_outs)

#                     # Determine status (Present or Absent) for the current day
#                     status = "Present" if check_ins.exists() else "Absent"

#                     # Store data for the current day in the timesheet_data dictionary
#                     timesheet_data[f"{worker.first_name} {worker.last_name}"][current_date.strftime("%Y-%m-%d")] = {
#                         "status": status,
#                         "effective_working_time": effective_working_time,
#                         "total_break_time": total_break_time,
#                         "agency": agency_name,
#                         "sub_category": subcategory_name
#                     }
#                 except ValueError:  # Handle if the day is out of range for the month
#                     pass

#         return Response(timesheet_data)

#     except Exception as e:
#         return Response({"error": str(e)}, status=400)


# def calculate_effective_working_time(check_ins, check_outs):
#     try:
#         # Calculate effective working time for a single day
#         total_working_time = timedelta(seconds=0)
#         for check_in, check_out in zip(check_ins, check_outs):
#             effective_working_time = check_out.created_at - check_in.created_at
#             if effective_working_time > timedelta(seconds=0):
#                 total_working_time += effective_working_time
#         return total_working_time.total_seconds()
#     except Exception as e:
#         return 0


# def calculate_total_break_time(check_ins, check_outs):
#     try:
#         # Calculate total break time for a single day
#         total_break_time = sum((check_out.created_at - check_in.created_at).total_seconds()
#                                for check_in, check_out in zip(check_ins, check_outs))
#         return total_break_time
#     except Exception as e:
#         return 0

@api_view(['POST'])
def calculate_monthly_contract_worker_timesheet_report(request):
    try:
        # Extract formData from request
        agency_id = request.data.get("agency")
        month = request.data.get("month")
        year = request.data.get("year")
        worker_ids = request.data.get("workers")

        if year is None or month is None:
            return Response({"error": "Year or month is missing from the request."}, status=400)

        # Convert month to its equivalent integer representation
        month_dict = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
            "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
            "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }
        month_int = month_dict.get(month)

        if month_int is None:
            return Response({"error": "Invalid month provided."}, status=400)

        # Convert year to integer if it's a valid integer
        try:
            year_int = int(year)
        except ValueError:
            return Response({"error": "Year must be a valid integer."}, status=400)

        # Get workers based on the provided IDs and conditions
        # Check if "All Workers" option is selected
        if worker_ids == ["All_Workers"]:
            # Fetch all workers
            print('inside all workers selected option ')
            workers = UserAccount.objects.filter(is_contract_worker=True)
        else:
            # Fetch workers based on the provided IDs and conditions
            if agency_id and worker_ids:
                workers = UserAccount.objects.filter(
                    id__in=worker_ids, agency_id=agency_id, is_contract_worker=True)
            elif agency_id:
                workers = UserAccount.objects.filter(
                    agency_id=agency_id, is_contract_worker=True)
            elif worker_ids:
                workers = UserAccount.objects.filter(
                    id__in=worker_ids, is_contract_worker=True)
            else:
                print('neither agency nor worker ids')
                workers = UserAccount.objects.filter(
                    is_contract_worker=True)

        # List to store timesheet data for each contract worker
        timesheet_data = []

        num_days_in_month = calendar.monthrange(year_int, month_int)[1]
        print('num of days in selected month', num_days_in_month)

        # Iterate through each worker
        for worker in workers:
            # Fetch agency and subcategory details for the current worker
            agency_name = worker.agency.name if worker.agency else None
            subcategory_name = worker.sub_category.name if worker.sub_category else None

            # Create dictionary for the contract worker
            contract_worker_data = {
                "contract_worker_name": f"{worker.first_name} {worker.last_name}",
                "agency": agency_name,
                "subcategory": subcategory_name
            }

            # Dictionary to store daily timesheet data
            daily_timesheet_data = {}

            for day in range(1, num_days_in_month + 1):
                try:
                    # Get the date of the current day in the loop
                    current_date = datetime.date(year_int, month_int, day)

                    # Get check-ins and check-outs for the current day
                    check_ins = CheckInAndOut.objects.filter(
                        user=worker, type='checkin', created_at__date=current_date)
                    check_outs = CheckInAndOut.objects.filter(
                        user=worker, type='checkout', created_at__date=current_date)

                    # Calculate total effective working time for the current day
                    effective_working_time = calculate_effective_working_time(
                        check_ins, check_outs)

                    # Calculate total break time for the current day
                    total_break_time = calculate_total_break_time(
                        check_ins, check_outs)

                    # Determine status (Present or Absent) for the current day
                    status = "Present" if check_ins.exists() else "Absent"

                    # Store daily timesheet data
                    daily_timesheet_data[current_date.strftime("%Y-%m-%d")] = {
                        "status": status,
                        "effective_working_time": effective_working_time,
                        "total_break_time": total_break_time
                    }
                except ValueError:  # Handle if the day is out of range for the month
                    pass

            # Add daily timesheet data to contract worker data
            contract_worker_data.update(daily_timesheet_data)

            # Append contract worker data to timesheet_data list
            timesheet_data.append(contract_worker_data)

        return Response(timesheet_data)

    except Exception as e:
        return Response({"error": str(e)}, status=400)


def calculate_effective_working_time(check_ins, check_outs):
    try:
        # Calculate effective working time for a single day
        total_working_time = timedelta(seconds=0)
        for check_in, check_out in zip(check_ins, check_outs):
            effective_working_time = check_out.created_at - check_in.created_at
            if effective_working_time > timedelta(seconds=0):
                total_working_time += effective_working_time
        return total_working_time.total_seconds()
    except Exception as e:
        return 0


def calculate_total_break_time(check_ins, check_outs):
    try:
        # Calculate total break time for a single day
        total_break_time = sum((check_out.created_at - check_in.created_at).total_seconds()
                               for check_in, check_out in zip(check_ins, check_outs))
        return total_break_time
    except Exception as e:
        return 0


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def parse_excel_contract_workers_creation(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        if excel_file.name.endswith('.xlsx'):
            try:
                df = pd.read_excel(excel_file)
                print(df.head())  # Print the first 5 rows of the DataFrame
                entries_created = 0
                entries_updated = 0  # Counter for updated entries
                for index, row in df.iterrows():
                    # Extracting data from each row
                    # Print row index being processed
                    # print(f"Processing row {index + 1}...")
                    first_name = row['First Name']
                    last_name = row['Last Name']
                    subcategory_name = row['Subcategory']
                    agency_name = row['Agency Name']
                    mobile_number = row.get('Mobile Number (Optional)', None)
                    dob = row.get('DOB(Optional)', None)

                    # Check if dob is NaT (missing or invalid date)
                    if pd.isna(dob):
                        dob = None  # Set dob to None
                    # Check if last name is empty, set to None
                    if pd.isna(last_name) or last_name == "":
                        last_name = None

                    # Convert mobile number to string to remove decimal part
                    if pd.notna(mobile_number):
                        mobile_number = str(int(mobile_number))
                    else:
                        mobile_number = None

                    # Print extracted data
                    print(
                        f"First Name: {first_name}, Last Name: {last_name}, Subcategory: {subcategory_name}, Agency: {agency_name}, DOB: {dob}, Mobile Number :{mobile_number}")

                    # Retrieve or create SubCategory and Agency objects
                    subcategory, _ = SubCategory.objects.get_or_create(
                        name=subcategory_name)
                    agency, _ = Agency.objects.get_or_create(name=agency_name)

                    # Creating email and password
                    email = f"{first_name.replace(' ', '').lower()}@automhr.com"
                    password = "password"

                    # Update or create UserAccount object
                    user_account, created = UserAccount.objects.update_or_create(
                        email=email,
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'sub_category': subcategory,
                            'agency': agency,
                            'phone_number': mobile_number,
                            'dob': dob,
                            'is_contract_worker': True
                        }
                    )

                    # Increment counters based on operation
                    if created:
                        entries_created += 1
                    else:
                        entries_updated += 1

                    # Print created/updated user account object
                    print(f"User account created/updated: {user_account}")

                print(
                    f"{entries_created} entries created and {entries_updated} entries updated successfully.")
                return Response({'message': f'{entries_created} entries created and {entries_updated} entries updated successfully.'})
            except Exception as e:
                print(f"An error occurred: {e}")  # Print the exception
                return Response({'error': str(e)}, status=500)
        else:
            return Response({'error': 'Please upload a valid Excel file.'}, status=400)
    else:
        return Response({'error': 'Invalid request method or file not provided.'}, status=400)
