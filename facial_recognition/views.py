from decimal import Decimal
from itertools import zip_longest
import random
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
from django.utils import timezone
from datetime import datetime, timedelta


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
from automhrai.utils import upload_file_to_s3, upload_file_to_s3_2
from django.conf import settings
import calendar
from django.db.models import Count
import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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
            end_date = datetime.datetime.now().date()

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


@api_view(['GET', 'POST'])
def get_contract_worker_timesheet_attendance_for_bill_generation_for_specific_date(request):
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

        date_str = request.data.get('date')

        if not date_str:
            return Response({'error': 'Date not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format, should be YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        work_time, break_time, entries = calculate_timesheet_for_date(
            user, date)

        user_data = {
            'user_info': user.id,
            'date': date,
            'work_time': work_time,
            'break_time': break_time,
            'entries': entries
        }

        return Response({'user_data': user_data}, status=status.HTTP_200_OK)


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

            full_name = worker.first_name
            if worker.last_name:
                full_name += " " + worker.last_name

            # Create dictionary for the contract worker
            contract_worker_data = {
                "contract_worker_name": full_name,
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


def generate_sequential_number():
    # Assuming you have a function to generate unique sequential numbers
    return random.randint(1000, 9999)


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

                    # Check if email already exists in the database
                    existing_emails = UserAccount.objects.filter(email=email)

                    if existing_emails.exists():
                        # Generate a sequential number
                        sequential_number = generate_sequential_number()
                        email = f"{first_name.replace(' ', '').lower()}{sequential_number}@automhr.com"

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


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def create_check_in_out(request):
    if request.method == 'POST':
        try:
            user = UserAccount.objects.get(email=request.data['email'])
            location = Location.objects.get(id=request.data['location_id'])
            today = timezone.now().date()

            latest_check_in_out = CheckInAndOut.objects.filter(
                user=user, location=location, created_at__date=today,).order_by('-created_at').first()

            if latest_check_in_out and latest_check_in_out.type == 'checkin':
                type = 'checkout'
            else:
                type = 'checkin'

            check_in_out = CheckInAndOut.objects.create(
                user=user, type=type, location=location)

            file = request.data.get('image')
            file_content = file.read()
            file_name = file.name

            try:
                image_url = upload_file_to_s3_2(
                    file_content, file_name, settings.AWS_STORAGE_BUCKET_NAME)
                if not image_url:
                    return Response({'error': 'Failed to upload image to S3'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                check_in_out.image = image_url
                check_in_out.save()

                serializer = CheckInAndOutSerializer(check_in_out)

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'check_in_out_create_group',
                    {
                        'type': 'send_check_in_out_data',
                        'check_in_out_data': serializer.data,
                    }
                )

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print("Exception occurred during file upload:", e)
                return Response({'error': 'Failed to upload image to S3'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except UserAccount.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Location.DoesNotExist:
            return Response({'error': 'Location does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("Exception occurred:", e)
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_all_attendance_billing(request):
    try:
        attendance_billing = AttendanceBilling.objects.all()
        serializer = ContractWorkerBillApprovalSerializer(
            attendance_billing, many=True)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({'message': str(e)}, status=500)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def create_attendance_billing(request):
    try:
        for data in request.data:
            user = UserAccount.objects.get(id=data['worker_id'])
            date = datetime.datetime.now().date()
            hourly_rate = data['hourly_rate']
            working_hours = data['total_normal_shift_hours']
            extra_hours = data['total_extra_shift_hours']
            working_bill_amount = data['total_working_bill']
            extra_bill_amount = data['total_extra_bill']
            total_hours = data['total_hours']
            total_bill_amount = data['total_bill']

            AttendanceBilling.objects.create(
                user=user,
                date=date,
                hourly_rate=hourly_rate,
                working_hours=working_hours,
                extra_hours=extra_hours,
                working_bill_amount=working_bill_amount,
                extra_bill_amount=extra_bill_amount,
                total_hours=total_hours,
                total_bill_amount=total_bill_amount,
            )

        return Response({'message': 'Attendance billing created successfully'}, status=201)

    except UserAccount.DoesNotExist:
        return Response({'message': 'User not found'}, status=404)
    except Exception as e:
        return Response({'message': str(e)}, status=500)


@api_view(['PUT'])
def update_attendance_billing_status(request):
    try:
        selected_rows = request.data.get('selected_rows', [])
        action = request.data.get('action')

        if action not in [AttendanceBilling.PENDING, AttendanceBilling.APPROVED, AttendanceBilling.REJECTED]:
            return Response({'message': 'Invalid action'}, status=400)

        updated_rows = []
        for row in selected_rows:
            try:
                billing = AttendanceBilling.objects.get(id=row['id'])
                billing.status = action
                billing.save()
                updated_rows.append(billing.id)
            except AttendanceBilling.DoesNotExist:
                continue

        if updated_rows:
            return Response({'message': 'Status updated successfully', 'updated_rows': updated_rows}, status=200)
        else:
            return Response({'message': 'No records updated'}, status=400)

    except Exception as e:
        return Response({'message': str(e)}, status=500)


# @api_view(['POST'])
# @authentication_classes([])
# @permission_classes([])
# def calculate_cumulative_contract_worker_timesheet(request):
#     try:
#         velankani_company = Company.objects.get(name='Velankani')
#         cut_off_time = velankani_company.cut_off_time
#         print('cut_off_time from database:', cut_off_time)

#         agency_id = request.data.get("agency")
#         from_date_str = request.data.get("fromDate")
#         to_date_str = request.data.get("toDate")
#         worker_ids = request.data.get("workers")

#         # Validate date inputs
#         try:
#             from_date = datetime.datetime.strptime(
#                 from_date_str, "%Y-%m-%d").date()
#             to_date = datetime.datetime.strptime(
#                 to_date_str, "%Y-%m-%d").date()
#         except ValueError:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

#         if from_date > to_date:
#             return Response({"error": "Invalid date range. 'From' date should be before 'To' date."}, status=400)

#         # Get workers based on the provided IDs and conditions
#         if worker_ids == ["All_Workers"]:
#             if agency_id:
#                 # If "All_Workers" is selected along with a specific agency
#                 workers = UserAccount.objects.filter(
#                     agency_id=agency_id, is_contract_worker=True)
#             else:
#                 # If "All_Workers" is selected without any specific agency
#                 workers = UserAccount.objects.filter(is_contract_worker=True)
#         else:
#             if agency_id and worker_ids:
#                 # If specific worker IDs are selected along with a specific agency
#                 workers = UserAccount.objects.filter(
#                     id__in=worker_ids, agency_id=agency_id, is_contract_worker=True)
#             elif agency_id:
#                 # If only a specific agency is selected
#                 workers = UserAccount.objects.filter(
#                     agency_id=agency_id, is_contract_worker=True)
#             elif worker_ids:
#                 # If only specific worker IDs are selected
#                 workers = UserAccount.objects.filter(
#                     id__in=worker_ids, is_contract_worker=True)
#             else:
#                 # If no specific agency or worker IDs are provided
#                 workers = UserAccount.objects.filter(is_contract_worker=True)

#         # List to store cumulative timesheet data for each contract worker
#         cumulative_timesheet_data = []

#         # Iterate through each worker

#         for worker in workers:
#             worker_id = worker.id
#             agency_name = worker.agency.name if worker.agency else None
#             subcategory_name = worker.sub_category.name if worker.sub_category else None
#             hourly_rate = worker.hourly_rate if worker.hourly_rate else Decimal(
#                 '0.0')

#             full_name = worker.first_name
#             if worker.last_name:
#                 full_name += " " + worker.last_name

#             # Initialize total values
#             total_normal_shift_hours = Decimal(0)
#             total_extra_shift_hours = Decimal(0)
#             total_hours = Decimal(0)
#             total_working_bill = Decimal(0)
#             total_extra_bill = Decimal(0)

#             current_date = from_date
#             print('current worker', worker_id)
#             while current_date <= to_date:
#                 print('Processing date:', current_date)
#                 try:
#                     print('for user', worker_id)
#                     whole_day_check_ins = CheckInAndOut.objects.filter(
#                         user=worker, type='checkin', created_at__date=current_date)
#                     print('whole day check-ins', whole_day_check_ins)
#                     whole_day_check_outs = CheckInAndOut.objects.filter(
#                         user=worker, type='checkout', created_at__date=current_date)
#                     print('whole day check-outs', whole_day_check_ins)
#                     whole_day_break_ins = BreakInAndOut.objects.filter(
#                         user=worker, type='breakin', created_at__date=current_date)
#                     print('whole day break-ins', whole_day_break_ins)
#                     whole_day_break_outs = BreakInAndOut.objects.filter(
#                         user=worker, type='breakout', created_at__date=current_date)
#                     print('whole day break-outs', whole_day_break_outs)

#                     effective_working_time_whole_day = calculate_effective_working_time_new(
#                         whole_day_check_ins, whole_day_check_outs, whole_day_break_ins, whole_day_break_outs)
#                     print('effective working time whole day',
#                           effective_working_time_whole_day)

#                     check_ins_after_cutoff_time = CheckInAndOut.objects.filter(
#                         user=worker, type='checkin', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                     check_outs_after_cutoff_time = CheckInAndOut.objects.filter(
#                         user=worker, type='checkout', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                     break_ins_after_cutoff_time = BreakInAndOut.objects.filter(
#                         user=worker, type='breakin', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                     break_outs_after_cutoff_time = BreakInAndOut.objects.filter(
#                         user=worker, type='breakout', created_at__date=current_date, created_at__time__gte=cut_off_time)

#                     events_after_cutoff_time = list(check_ins_after_cutoff_time) + list(check_outs_after_cutoff_time) + list(
#                         break_ins_after_cutoff_time) + list(break_outs_after_cutoff_time)
#                     events_after_cutoff_time.sort(
#                         key=lambda event: event.created_at)

#                     extra_working_time = calculate_extra_shift_time(
#                         events_after_cutoff_time, cut_off_time)
#                     print('extra working time', extra_working_time)
#                     # Update total values
#                     total_extra_shift_hours += Decimal(extra_working_time)
#                     print('total extra shift hours',
#                           total_extra_shift_hours)
#                     total_normal_shift_hours += Decimal(
#                         effective_working_time_whole_day)-total_extra_shift_hours
#                     print('total normal shift hours',
#                           total_normal_shift_hours)
#                 except ValueError:
#                     pass

#                 current_date += datetime.timedelta(days=1)

#             total_working_bill = hourly_rate * total_normal_shift_hours
#             total_extra_bill = hourly_rate * total_extra_shift_hours
#             total_bill = total_working_bill + total_extra_bill
#             total_hours = total_normal_shift_hours+total_extra_shift_hours

#             contract_worker_data = {
#                 "worker_id": worker_id,
#                 "contract_worker_name": full_name,
#                 "agency": agency_name,
#                 "subcategory": subcategory_name,
#                 # Ensure it's serialized correctly
#                 "hourly_rate": float(hourly_rate),
#                 "total_normal_shift_hours": float(total_normal_shift_hours),
#                 "total_extra_shift_hours": float(total_extra_shift_hours),
#                 "total_hours": float(total_hours),
#                 "total_working_bill": float(total_working_bill),
#                 "total_extra_bill": float(total_extra_bill),
#                 "total_bill": float(total_bill)
#             }
#             print(contract_worker_data)

#             cumulative_timesheet_data.append(contract_worker_data)

#         return Response(cumulative_timesheet_data)

#     except Exception as e:
#         return Response({"error": str(e)}, status=400)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def calculate_cumulative_contract_worker_timesheet(request):
    try:
        velankani_company = Company.objects.get(name='Velankani')
        cut_off_time = velankani_company.cut_off_time
        print('cut_off_time from database:', cut_off_time)

        agency_id = request.data.get("agency")
        from_date_str = request.data.get("fromDate")
        to_date_str = request.data.get("toDate")
        worker_ids = request.data.get("workers")

        # Validate date inputs
        try:
            from_date = datetime.datetime.strptime(
                from_date_str, "%Y-%m-%d").date()
            to_date = datetime.datetime.strptime(
                to_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if from_date > to_date:
            return Response({"error": "Invalid date range. 'From' date should be before 'To' date."}, status=400)

        # Get workers based on the provided IDs and conditions
        if worker_ids == ["All_Workers"]:
            if agency_id:
                workers = UserAccount.objects.filter(
                    agency_id=agency_id, is_contract_worker=True)
            else:
                workers = UserAccount.objects.filter(is_contract_worker=True)
        else:
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
                workers = UserAccount.objects.filter(is_contract_worker=True)

        cumulative_timesheet_data = []

        for worker in workers:
            worker_id = worker.id
            agency_name = worker.agency.name if worker.agency else None
            subcategory_name = worker.sub_category.name if worker.sub_category else None
            hourly_rate = worker.hourly_rate if worker.hourly_rate else Decimal(
                '0.0')

            full_name = worker.first_name
            if worker.last_name:
                full_name += " " + worker.last_name

            total_normal_shift_hours = Decimal(0)
            total_extra_shift_hours = Decimal(0)
            total_hours = Decimal(0)
            total_working_bill = Decimal(0)
            total_extra_bill = Decimal(0)

            current_date = from_date
            print('current worker', worker_id)
            while current_date <= to_date:
                print('Processing date:', current_date)
                try:
                    whole_day_check_ins = CheckInAndOut.objects.filter(
                        user=worker, type='checkin', created_at__date=current_date)
                    whole_day_check_outs = CheckInAndOut.objects.filter(
                        user=worker, type='checkout', created_at__date=current_date)
                    whole_day_break_ins = BreakInAndOut.objects.filter(
                        user=worker, type='breakin', created_at__date=current_date)
                    whole_day_break_outs = BreakInAndOut.objects.filter(
                        user=worker, type='breakout', created_at__date=current_date)

                    if whole_day_check_ins or whole_day_check_outs or whole_day_break_ins or whole_day_break_outs:
                        effective_working_time_whole_day = calculate_effective_working_time_new(
                            whole_day_check_ins, whole_day_check_outs, whole_day_break_ins, whole_day_break_outs)
                        print('effective working time whole day:',
                              effective_working_time_whole_day)

                        check_ins_after_cutoff_time = CheckInAndOut.objects.filter(
                            user=worker, type='checkin', created_at__date=current_date, created_at__time__gte=cut_off_time)
                        check_outs_after_cutoff_time = CheckInAndOut.objects.filter(
                            user=worker, type='checkout', created_at__date=current_date, created_at__time__gte=cut_off_time)
                        break_ins_after_cutoff_time = BreakInAndOut.objects.filter(
                            user=worker, type='breakin', created_at__date=current_date, created_at__time__gte=cut_off_time)
                        break_outs_after_cutoff_time = BreakInAndOut.objects.filter(
                            user=worker, type='breakout', created_at__date=current_date, created_at__time__gte=cut_off_time)

                        events_after_cutoff_time = list(check_ins_after_cutoff_time) + list(check_outs_after_cutoff_time) + list(
                            break_ins_after_cutoff_time) + list(break_outs_after_cutoff_time)
                        events_after_cutoff_time.sort(
                            key=lambda event: event.created_at)

                        extra_working_time = calculate_extra_shift_time(
                            events_after_cutoff_time, cut_off_time)
                        print('extra working time:', extra_working_time)

                        total_extra_shift_hours += Decimal(extra_working_time)
                        total_normal_shift_hours += Decimal(
                            effective_working_time_whole_day) - Decimal(extra_working_time)

                        print('total extra shift hours:',
                              total_extra_shift_hours)
                        print('total normal shift hours:',
                              total_normal_shift_hours)
                except ValueError:
                    pass

                current_date += datetime.timedelta(days=1)

            total_working_bill = hourly_rate * total_normal_shift_hours
            total_extra_bill = hourly_rate * total_extra_shift_hours
            total_bill = total_working_bill + total_extra_bill
            total_hours = total_normal_shift_hours + total_extra_shift_hours

            contract_worker_data = {
                "worker_id": worker_id,
                "contract_worker_name": full_name,
                "agency": agency_name,
                "subcategory": subcategory_name,
                "hourly_rate": float(hourly_rate),
                "total_normal_shift_hours": float(total_normal_shift_hours),
                "total_extra_shift_hours": float(total_extra_shift_hours),
                "total_hours": float(total_hours),
                "total_working_bill": float(total_working_bill),
                "total_extra_bill": float(total_extra_bill),
                "total_bill": float(total_bill)
            }
            print(contract_worker_data)

            cumulative_timesheet_data.append(contract_worker_data)

        return Response(cumulative_timesheet_data)

    except Exception as e:
        return Response({"error": str(e)}, status=400)


# @api_view(['POST'])
# @authentication_classes([])
# @permission_classes([])
# def calculate_daily_contract_worker_timesheet(request):
#     try:
#         velankani_company = Company.objects.get(name='Velankani')
#         cut_off_time = velankani_company.cut_off_time


#         print('cut_off_time from database:', cut_off_time)

#         agency_id = request.data.get("agency")
#         from_date_str = request.data.get("fromDate")
#         to_date_str = request.data.get("toDate")
#         worker_ids = request.data.get("workers")

#         # Validate date inputs
#         try:
#             from_date = datetime.datetime.strptime(
#                 from_date_str, "%Y-%m-%d").date()
#             to_date = datetime.datetime.strptime(
#                 to_date_str, "%Y-%m-%d").date()
#         except ValueError:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

#         if from_date > to_date:
#             return Response({"error": "Invalid date range. 'From' date should be before 'To' date."}, status=400)

#         # Get workers based on the provided IDs and conditions
#         if worker_ids == ["All_Workers"]:
#             # Fetch all workers
#             workers = UserAccount.objects.filter(is_contract_worker=True)
#         else:
#             # Fetch workers based on the provided IDs and conditions
#             if agency_id and worker_ids:
#                 workers = UserAccount.objects.filter(
#                     id__in=worker_ids, agency_id=agency_id, is_contract_worker=True)
#             elif agency_id:
#                 workers = UserAccount.objects.filter(
#                     agency_id=agency_id, is_contract_worker=True)
#             elif worker_ids:
#                 workers = UserAccount.objects.filter(
#                     id__in=worker_ids, is_contract_worker=True)
#             else:
#                 workers = UserAccount.objects.filter(
#                     is_contract_worker=True)

#         # List to store timesheet data for each contract worker
#         timesheet_data = []

#         # Iterate through each worker
#         for worker in workers:
#             # Fetch agency and subcategory details for the current worker
#             agency_name = worker.agency.name if worker.agency else None
#             subcategory_name = worker.sub_category.name if worker.sub_category else None
#             hourly_rate = worker.hourly_rate if worker.hourly_rate else None

#             full_name = worker.first_name
#             if worker.last_name:
#                 full_name += " " + worker.last_name

#             # Create dictionary for the contract worker
#             contract_worker_data = {
#                 "contract_worker_name": full_name,
#                 "agency": agency_name,
#                 "subcategory": subcategory_name,
#                 "hourly_rate": hourly_rate
#             }

#             # Dictionary to store daily timesheet data
#             daily_timesheet_data = {}

#             # Iterate through each day within the date range
#             current_date = from_date
#             while current_date <= to_date:
#                 try:
#                     # # Get check-ins, check-outs, break-ins, and break-outs for the current day until 6 PM
#                     whole_day_check_ins = CheckInAndOut.objects.filter(
#                         user=worker, type='checkin', created_at__date=current_date)
#                     whole_day_check_outs = CheckInAndOut.objects.filter(
#                         user=worker, type='checkout', created_at__date=current_date)
#                     whole_day_break_ins = BreakInAndOut.objects.filter(
#                         user=worker, type='breakin', created_at__date=current_date)
#                     whole_day_break_outs = BreakInAndOut.objects.filter(
#                         user=worker, type='breakout', created_at__date=current_date)

#                     effective_working_time_whole_day = calculate_effective_working_time_new(
#                         whole_day_check_ins, whole_day_check_outs, whole_day_break_ins, whole_day_break_outs)

#                     print('effective_working_time_whole_day',
#                           effective_working_time_whole_day)

#                     # check_ins = CheckInAndOut.objects.filter(
#                     #     user=worker, type='checkin', created_at__date=current_date, created_at__time__lt=datetime.time(18, 0))
#                     # check_outs = CheckInAndOut.objects.filter(
#                     #     user=worker, type='checkout', created_at__date=current_date, created_at__time__lt=datetime.time(18, 0))
#                     # break_ins = BreakInAndOut.objects.filter(
#                     #     user=worker, type='breakin', created_at__date=current_date, created_at__time__lt=datetime.time(18, 0))
#                     # break_outs = BreakInAndOut.objects.filter(
#                     #     user=worker, type='breakout', created_at__date=current_date, created_at__time__lt=datetime.time(18, 0))

#                     # # Calculate total effective working time until 6 PM for the current day
#                     # effective_working_time = calculate_effective_working_time_new(
#                     #     check_ins, check_outs, break_ins, break_outs)

#                     # Filter check-ins, check-outs, break-ins, and break-outs after 6 PM
#                     check_ins_after_cutoff_time = CheckInAndOut.objects.filter(
#                         user=worker, type='checkin', created_at__date=current_date, created_at__time__gte=cut_off_time)

#                     print('check in after cutoff_time',
#                           check_ins_after_cutoff_time)
#                     check_outs_after_cutoff_time = CheckInAndOut.objects.filter(
#                         user=worker, type='checkout', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                     break_ins_after_cutoff_time = BreakInAndOut.objects.filter(
#                         user=worker, type='breakin', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                     break_outs_after_cutoff_time = BreakInAndOut.objects.filter(
#                         user=worker, type='breakout', created_at__date=current_date, created_at__time__gte=cut_off_time)

#                     # Combine and sort events after cutoff_time PM
#                     events_after_cutoff_time = list(check_ins_after_cutoff_time) + list(check_outs_after_cutoff_time) + list(
#                         break_ins_after_cutoff_time) + list(break_outs_after_cutoff_time)
#                     events_after_cutoff_time.sort(
#                         key=lambda event: event.created_at)

#                     # Calculate effective working time after cutoff_time PM
#                     extra_shift_working_time = calculate_extra_shift_time(
#                         events_after_cutoff_time,  cut_off_time)

#                     print('extra_working_time',
#                           extra_shift_working_time)

#                     # Determine status (Present or Absent) for the whole day
#                     status = "Present" if whole_day_check_ins.exists(
#                     ) or check_ins_after_cutoff_time.exists() else "Absent"
#                     # Ensure all calculations use Decimal
#                     working_bill = hourly_rate * \
#                         Decimal(effective_working_time_whole_day)
#                     extra_bill = hourly_rate * \
#                         Decimal(extra_shift_working_time)
#                     total_bill = working_bill + extra_bill

#                     # Store daily timesheet data
#                     daily_timesheet_data[current_date.strftime("%Y-%m-%d")] = {
#                         "status": status,
#                         "normal_shift_hours": effective_working_time_whole_day,
#                         "extra_shift_hours":  extra_shift_working_time,
#                         # Convert to float for serialization
#                         "working_bill": float(working_bill),
#                         # Convert to float for serialization
#                         "extra_bill": float(extra_bill),
#                         "total_bill": float(total_bill)
#                     }
#                 except ValueError:  # Handle if there are no check-ins or check-outs
#                     pass

#                 # Move to the next day
#                 current_date += timedelta(days=1)

#             # Add daily timesheet data to contract worker data
#             contract_worker_data.update(daily_timesheet_data)

#             # Append contract worker data to timesheet_data list
#             timesheet_data.append(contract_worker_data)

#         return Response(timesheet_data)

#     except Exception as e:
#         return Response({"error": str(e)}, status=400)


# @api_view(['POST'])
# @authentication_classes([])
# @permission_classes([])
# def calculate_daily_contract_worker_timesheet(request):
#     try:
#         velankani_company = Company.objects.get(name='Velankani')
#         cut_off_time = velankani_company.cut_off_time

#         agency_id = request.data.get("agency")
#         from_date_str = request.data.get("fromDate")
#         print(from_date_str)
#         to_date_str = request.data.get("toDate")
#         worker_ids = request.data.get("workers")

#         # Validate date inputs
#         try:
#             from_date = datetime.datetime.strptime(
#                 from_date_str, "%Y-%m-%d").date()

#             print('from_Date', from_date)
#             to_date = datetime.datetime.strptime(
#                 to_date_str, "%Y-%m-%d").date()
#             print('to_date', to_date)
#         except ValueError:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

#         if from_date > to_date:
#             return Response({"error": "Invalid date range. 'From' date should be before 'To' date."}, status=400)

#         # Get workers based on the provided IDs and conditions
#         if worker_ids == ["All_Workers"]:
#             workers = UserAccount.objects.filter(is_contract_worker=True)
#         else:
#             if agency_id and worker_ids:
#                 workers = UserAccount.objects.filter(
#                     id__in=worker_ids, agency_id=agency_id, is_contract_worker=True)
#             elif agency_id:
#                 workers = UserAccount.objects.filter(
#                     agency_id=agency_id, is_contract_worker=True)
#             elif worker_ids:
#                 workers = UserAccount.objects.filter(
#                     id__in=worker_ids, is_contract_worker=True)
#             else:
#                 workers = UserAccount.objects.filter(is_contract_worker=True)

#         # List to store timesheet data for each contract worker
#         timesheet_data = []

#         # Iterate through each worker
#         for worker in workers:
#             agency_name = worker.agency.name if worker.agency else None
#             subcategory_name = worker.sub_category.name if worker.sub_category else None
#             hourly_rate = worker.hourly_rate if worker.hourly_rate else None

#             full_name = worker.first_name
#             if worker.last_name:
#                 full_name += " " + worker.last_name

#             # Iterate through each day within the date range
#             current_date = from_date
#             while current_date <= to_date:
#                 try:
#                     whole_day_check_ins = CheckInAndOut.objects.filter(
#                         user=worker, type='checkin', created_at__date=current_date)
#                     whole_day_check_outs = CheckInAndOut.objects.filter(
#                         user=worker, type='checkout', created_at__date=current_date)
#                     whole_day_break_ins = BreakInAndOut.objects.filter(
#                         user=worker, type='breakin', created_at__date=current_date)
#                     whole_day_break_outs = BreakInAndOut.objects.filter(
#                         user=worker, type='breakout', created_at__date=current_date)

#                     effective_working_time_whole_day = calculate_effective_working_time_new(
#                         whole_day_check_ins, whole_day_check_outs, whole_day_break_ins, whole_day_break_outs)

#                     check_ins_after_cutoff_time = CheckInAndOut.objects.filter(
#                         user=worker, type='checkin', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                     check_outs_after_cutoff_time = CheckInAndOut.objects.filter(
#                         user=worker, type='checkout', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                     break_ins_after_cutoff_time = BreakInAndOut.objects.filter(
#                         user=worker, type='breakin', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                     break_outs_after_cutoff_time = BreakInAndOut.objects.filter(
#                         user=worker, type='breakout', created_at__date=current_date, created_at__time__gte=cut_off_time)

#                     events_after_cutoff_time = list(check_ins_after_cutoff_time) + list(check_outs_after_cutoff_time) + list(
#                         break_ins_after_cutoff_time) + list(break_outs_after_cutoff_time)
#                     events_after_cutoff_time.sort(
#                         key=lambda event: event.created_at)

#                     extra_shift_working_time = calculate_extra_shift_time(
#                         events_after_cutoff_time, cut_off_time)

#                     status = "Present" if whole_day_check_ins.exists(
#                     ) or check_ins_after_cutoff_time.exists() else "Absent"
#                     working_bill = hourly_rate * \
#                         Decimal(effective_working_time_whole_day)
#                     extra_bill = hourly_rate * \
#                         Decimal(extra_shift_working_time)
#                     total_bill = working_bill + extra_bill

#                     # Store daily timesheet data
#                     daily_timesheet_entry = {
#                         "contract_worker_name": full_name,
#                         "agency": agency_name,
#                         "subcategory": subcategory_name,
#                         "hourly_rate": hourly_rate,
#                         "date": current_date.strftime("%Y-%m-%d"),
#                         "status": status,
#                         "normal_shift_hours": effective_working_time_whole_day,
#                         "extra_shift_hours": extra_shift_working_time,
#                         "working_bill": float(working_bill),
#                         "extra_bill": float(extra_bill),
#                         "total_bill": float(total_bill)
#                     }

#                     timesheet_data.append(daily_timesheet_entry)

#                 except ValueError:
#                     pass

#                 current_date += timedelta(days=1)

#         return Response(timesheet_data)

#     except Exception as e:
#         return Response({"error": str(e)}, status=400)


# @api_view(['POST'])
# @authentication_classes([])
# @permission_classes([])
# def calculate_daily_contract_worker_timesheet(request, worker_id):
#     try:
#         print('sasasasa')
#         velankani_company = Company.objects.get(name='Velankani')
#         cut_off_time = velankani_company.cut_off_time

#         # agency_id = request.data.get("agency")
#         # Retrieve fromDate and toDate from request.data

#         from_date_str = request.data.get("fromDate")

#         print('form_Date_str comign fro mfrotn end', from_date_str)
#         to_date_str = request.data.get("toDate")

#         print('to_Date_str comign fro mfrotn end', to_date_str)

#         # worker_id = request.data.get("worker")
#         if not from_date_str or not to_date_str:
#             return Response({"error": "fromDate and toDate are required fields."}, status=400)

#         # Validate date inputs
#         try:
#             # from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
#             # to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
#             from_date = datetime.datetime.strptime(
#                 from_date_str, "%Y-%m-%d").date()

#             print('from_Date', from_date)
#             to_date = datetime.datetime.strptime(
#                 to_date_str, "%Y-%m-%d").date()
#             print('to_date', to_date)

#         except ValueError:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

#         if from_date > to_date:
#             return Response({"error": "Invalid date range. 'From' date should be before 'To' date."}, status=400)

#         # Get the worker based on the provided ID and conditions
#         try:
#             worker = UserAccount.objects.get(
#                 id=worker_id, is_contract_worker=True)
#         except UserAccount.DoesNotExist:
#             return Response({"error": "Worker not found or not a contract worker."}, status=404)

#         agency_name = worker.agency.name if worker.agency else None
#         subcategory_name = worker.sub_category.name if worker.sub_category else None
#         hourly_rate = worker.hourly_rate if worker.hourly_rate else None

#         full_name = worker.first_name
#         if worker.last_name:
#             full_name += " " + worker.last_name

#         # List to store timesheet data for the contract worker
#         timesheet_data = []

#         # Iterate through each day within the date range
#         current_date = from_date
#         while current_date <= to_date:
#             try:
#                 whole_day_check_ins = CheckInAndOut.objects.filter(
#                     user=worker, type='checkin', created_at__date=current_date)
#                 whole_day_check_outs = CheckInAndOut.objects.filter(
#                     user=worker, type='checkout', created_at__date=current_date)
#                 whole_day_break_ins = BreakInAndOut.objects.filter(
#                     user=worker, type='breakin', created_at__date=current_date)
#                 whole_day_break_outs = BreakInAndOut.objects.filter(
#                     user=worker, type='breakout', created_at__date=current_date)

#                 effective_working_time_whole_day = calculate_effective_working_time_new(
#                     whole_day_check_ins, whole_day_check_outs, whole_day_break_ins, whole_day_break_outs)

#                 check_ins_after_cutoff_time = CheckInAndOut.objects.filter(
#                     user=worker, type='checkin', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                 check_outs_after_cutoff_time = CheckInAndOut.objects.filter(
#                     user=worker, type='checkout', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                 break_ins_after_cutoff_time = BreakInAndOut.objects.filter(
#                     user=worker, type='breakin', created_at__date=current_date, created_at__time__gte=cut_off_time)
#                 break_outs_after_cutoff_time = BreakInAndOut.objects.filter(
#                     user=worker, type='breakout', created_at__date=current_date, created_at__time__gte=cut_off_time)

#                 events_after_cutoff_time = list(check_ins_after_cutoff_time) + list(check_outs_after_cutoff_time) + list(
#                     break_ins_after_cutoff_time) + list(break_outs_after_cutoff_time)
#                 events_after_cutoff_time.sort(
#                     key=lambda event: event.created_at)

#                 extra_shift_working_time = calculate_extra_shift_time(
#                     events_after_cutoff_time, cut_off_time)

#                 status = "Present" if whole_day_check_ins.exists(
#                 ) or check_ins_after_cutoff_time.exists() else "Absent"
#                 working_bill = hourly_rate * \
#                     (Decimal(effective_working_time_whole_day) -
#                      Decimal(extra_shift_working_time))
#                 extra_bill = hourly_rate * \
#                     Decimal(extra_shift_working_time)
#                 total_bill = working_bill + extra_bill
#                 total_hours = effective_working_time_whole_day+extra_shift_working_time

#                 # Store daily timesheet data
#                 daily_timesheet_entry = {
#                     "contract_worker_name": full_name,
#                     "worker_id": worker_id,
#                     "agency": agency_name,
#                     "subcategory": subcategory_name,
#                     "hourly_rate": hourly_rate,
#                     "date": current_date.strftime("%Y-%m-%d"),
#                     "status": status,
#                     "normal_shift_hours": effective_working_time_whole_day-extra_shift_working_time,
#                     "extra_shift_hours": extra_shift_working_time,
#                     "total_hours": total_hours,
#                     "working_bill": float(working_bill),
#                     "extra_bill": float(extra_bill),
#                     "total_bill": float(total_bill)
#                 }

#                 timesheet_data.append(daily_timesheet_entry)

#             except ValueError:
#                 pass

#             current_date += timedelta(days=1)

#         return Response(timesheet_data)

#     except Exception as e:
#         return Response({"error": str(e)}, status=400)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def calculate_daily_contract_worker_timesheet(request, worker_id):
    try:
        # Fetch cut-off time from company settings (assuming 'Velankani' company)
        velankani_company = Company.objects.get(name='Velankani')
        cut_off_time = velankani_company.cut_off_time

        # Retrieve fromDate and toDate from request.data
        from_date_str = request.data.get("fromDate")
        to_date_str = request.data.get("toDate")

        # Validate fromDate and toDate
        if not from_date_str or not to_date_str:
            return Response({"error": "fromDate and toDate are required fields."}, status=400)

        try:
            from_date = datetime.datetime.strptime(
                from_date_str, "%Y-%m-%d").date()
            to_date = datetime.datetime.strptime(
                to_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if from_date > to_date:
            return Response({"error": "Invalid date range. 'From' date should be before 'To' date."}, status=400)

        # Get the contract worker based on worker_id
        try:
            worker = UserAccount.objects.get(
                id=worker_id, is_contract_worker=True)
        except UserAccount.DoesNotExist:
            return Response({"error": "Worker not found or not a contract worker."}, status=404)

        # Retrieve worker details
        agency_name = worker.agency.name if worker.agency else None
        subcategory_name = worker.sub_category.name if worker.sub_category else None
        hourly_rate = worker.hourly_rate if worker.hourly_rate else None

        full_name = worker.get_full_name()

        # List to store timesheet data for the contract worker
        timesheet_data = []

        # Iterate through each day within the date range
        current_date = from_date
        while current_date <= to_date:
            try:
                # Fetch check-ins and check-outs for the day
                whole_day_check_ins = CheckInAndOut.objects.filter(
                    user=worker, type='checkin', created_at__date=current_date
                )
                whole_day_check_outs = CheckInAndOut.objects.filter(
                    user=worker, type='checkout', created_at__date=current_date
                )

                # Fetch break-ins and break-outs for the day
                whole_day_break_ins = BreakInAndOut.objects.filter(
                    user=worker, type='breakin', created_at__date=current_date
                )
                whole_day_break_outs = BreakInAndOut.objects.filter(
                    user=worker, type='breakout', created_at__date=current_date
                )

                # Calculate effective working time for the whole day
                effective_working_time_whole_day = calculate_effective_working_time_new(
                    whole_day_check_ins, whole_day_check_outs, whole_day_break_ins, whole_day_break_outs
                )

                # Fetch check-ins and check-outs after cut-off time
                check_ins_after_cutoff_time = CheckInAndOut.objects.filter(
                    Q(user=worker, type='checkin') & Q(created_at__date=current_date) & Q(
                        created_at__time__gte=cut_off_time)
                )
                check_outs_after_cutoff_time = CheckInAndOut.objects.filter(
                    Q(user=worker, type='checkout') & Q(created_at__date=current_date) & Q(
                        created_at__time__gte=cut_off_time)
                )

                # Fetch break-ins and break-outs after cut-off time
                break_ins_after_cutoff_time = BreakInAndOut.objects.filter(
                    Q(user=worker, type='breakin') & Q(created_at__date=current_date) & Q(
                        created_at__time__gte=cut_off_time)
                )
                break_outs_after_cutoff_time = BreakInAndOut.objects.filter(
                    Q(user=worker, type='breakout') & Q(created_at__date=current_date) & Q(
                        created_at__time__gte=cut_off_time)
                )

                # Combine all events after cut-off time and sort by timestamp
                events_after_cutoff_time = list(check_ins_after_cutoff_time) + list(check_outs_after_cutoff_time) + list(
                    break_ins_after_cutoff_time) + list(break_outs_after_cutoff_time)
                events_after_cutoff_time.sort(
                    key=lambda event: event.created_at)

                # Calculate extra shift working time after cut-off time
                extra_shift_working_time = calculate_extra_shift_time(
                    events_after_cutoff_time, cut_off_time
                )

                # Determine worker status for the day (Present or Absent)
                status = "Present" if whole_day_check_ins.exists(
                ) or check_ins_after_cutoff_time.exists() else "Absent"

                # Calculate billable amounts if hourly_rate is available
                if hourly_rate is not None:
                    working_bill = hourly_rate * \
                        (Decimal(effective_working_time_whole_day) -
                         Decimal(extra_shift_working_time))
                    extra_bill = hourly_rate * \
                        Decimal(extra_shift_working_time)
                    total_bill = working_bill + extra_bill
                else:
                    working_bill = Decimal(0)
                    extra_bill = Decimal(0)
                    total_bill = Decimal(0)

                total_hours = effective_working_time_whole_day + extra_shift_working_time

                # Create daily timesheet entry
                daily_timesheet_entry = {
                    "contract_worker_name": full_name,
                    "worker_id": worker_id,
                    "agency": agency_name,
                    "subcategory": subcategory_name,
                    "hourly_rate": float(hourly_rate) if hourly_rate is not None else None,
                    "date": current_date.strftime("%Y-%m-%d"),
                    "status": status,
                    "normal_shift_hours": effective_working_time_whole_day - extra_shift_working_time,
                    "extra_shift_hours": extra_shift_working_time,
                    "total_hours": total_hours,
                    "working_bill": float(working_bill),
                    "extra_bill": float(extra_bill),
                    "total_bill": float(total_bill)
                }

                timesheet_data.append(daily_timesheet_entry)

            except Exception as e:
                return Response({"error": str(e)}, status=400)

            current_date += timedelta(days=1)

        return Response(timesheet_data)

    except Exception as e:
        return Response({"error": str(e)}, status=400)


def calculate_effective_working_time_new(check_ins, check_outs, break_ins, break_outs):
    try:
        # Calculate effective working time until cutoff_time PM for a single day
        total_working_time = timedelta(seconds=0)
        breaks_time = timedelta(seconds=0)

        # print(check_ins)
        # print(check_ins[0])
        # print(check_ins[0].created_at)

        check_in_out_pairs = list(zip(check_ins, check_outs))

        break_in_out_pairs = list(zip(break_ins, break_outs))

        for check_in, check_out in check_in_out_pairs:
            if check_in.created_at < check_out.created_at:
                total_working_time += (check_out.created_at -
                                       check_in.created_at)

        for break_in, break_out in break_in_out_pairs:
            if break_in.created_at < break_out.created_at:
                breaks_time += (break_out.created_at - break_in.created_at)

        print('total working time', total_working_time)
        print(breaks_time)

        effective_working_time = total_working_time - breaks_time
        return effective_working_time.total_seconds()/3600
    except Exception as e:
        return 0


def calculate_extra_shift_time(events_after_cutoff_time, cut_off_time):
    try:
        # Calculate extra working time after cutoff_time PM for a single day

        print('events_after_cutoff_time', events_after_cutoff_time)
        total_working_time = timedelta(seconds=0)
        breaks_time = timedelta(seconds=0)

        if not events_after_cutoff_time:
            return 0

        first_event = events_after_cutoff_time[0]
        # print('first_event', first_event)
        # print(first_event.type)
        # print(first_event.created_at)
        # print(cut_off_time)
        event_date = first_event.created_at.date()
        # print(event_date)

        # Combine event_date with cut_off_time to create a datetime.datetime object
        cut_off_datetime = datetime.datetime.combine(event_date, cut_off_time)

        # Subtract 5 hours and 30 minutes using timedelta
        modified_cut_off_datetime_naive = cut_off_datetime - \
            datetime.timedelta(hours=5, minutes=30)

        # Convert modified_cut_off_datetime to timezone-aware datetime using the timezone info from first_event_created_at
        timezone_info = first_event.created_at.tzinfo
        modified_cut_off_datetime = modified_cut_off_datetime_naive.replace(
            tzinfo=timezone_info)
        # print('sasasas', modified_cut_off_datetime)
        # modified_cut_off_time = cut_off_datetime_utc - \
        #     datetime.timedelta(hours=5, minutes=30)
        # print('modified_cut_off_time', modified_cut_off_time)

        # print('first_event.created_At', first_event.created_at)
        # print('modified_cut_off_time', modified_cut_off_time)

        # If the first event is a checkout after cutoff_time PM, calculate the time from cutoff_time PM to this checkout
        if first_event.type == 'checkout' and first_event.created_at.time() >= modified_cut_off_datetime.time():
            print('inside if')

            total_working_time += (first_event.created_at -
                                   modified_cut_off_datetime)

            # Remove the first checkout event
            print('total_working_time inside if axaxax = ', total_working_time)
            events_after_cutoff_time = events_after_cutoff_time[1:]

        else:
            # Handle the case where the first event is not a checkout after cutoff_time PM
            # Optionally, you can manipulate events_after_cutoff_time here
            events_after_cutoff_time = events_after_cutoff_time

        # Calculate working time for remaining pairs of events
        check_in_out_pairs = []
        break_in_out_pairs = []

        # Using zip to iterate over pairs of events
        for current_event, next_event in zip(events_after_cutoff_time, events_after_cutoff_time[1:]):
            if current_event.type == 'checkin' and next_event.type == 'checkout':
                check_in_out_pairs.append((current_event, next_event))
            elif current_event.type == 'breakin' and next_event.type == 'breakout':
                break_in_out_pairs.append((current_event, next_event))

        for check_in, check_out in check_in_out_pairs:
            if check_in.created_at < check_out.created_at:
                total_working_time += (check_out.created_at -
                                       check_in.created_at)

        for break_in, break_out in break_in_out_pairs:
            if break_in.created_at < break_out.created_at:
                breaks_time += (break_out.created_at - break_in.created_at)

        extra_working_time = total_working_time - breaks_time
        return extra_working_time.total_seconds() / 3600

    except Exception as e:
        return 0
