# -*- coding: utf-8 -*-
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/cswsh/", consumers.CswshChatConsumer.as_asgi()),
    path("ws/dos/", consumers.DosConsumer.as_asgi()),
]
