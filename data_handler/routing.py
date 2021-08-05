from django.urls import path
from .consumers import RunModelConsumer

websocket_url_pattern = [
    path("dashboard/data/ws/run-model", RunModelConsumer.as_asgi()),
]