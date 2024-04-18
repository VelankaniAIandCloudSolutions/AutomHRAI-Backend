from celery import shared_task
from .utils import classify_face

@shared_task
def async_classify_face(img_path, threshold=0.4):
    from django.core.cache import cache
    cache_key = f"attendance_data_{img_path.split('/')[-1]}"
    attendance_data = cache.get(cache_key)
    if attendance_data:
        detected_user_email = classify_face(img_path, threshold)
        return detected_user_email, attendance_data
    return None, None
