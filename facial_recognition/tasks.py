from celery import shared_task
from .utils import classify_face 

@shared_task
def async_classify_face(img_path, threshold=0.4):
    return classify_face(img_path, threshold)
