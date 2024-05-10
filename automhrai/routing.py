from django.urls import path
from .consumers import *


websocket_urlpatterns = [
    path('ws/check-in-out/', CheckInOutConsumer.as_asgi()),
]
