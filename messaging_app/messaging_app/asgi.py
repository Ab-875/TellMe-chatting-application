"""
ASGI config for messaging_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from main_app.consumers import ChatConsumer
from pathlib import Path
from mimetypes import guess_type



STATIC_ROOT = Path(__file__).resolve().parent.parent / "main_app" / "static"

async def static_file_app(scope, receive, send):
    path = scope["path"]

    if not path.startswith("/static/"):
        await django_asgi_app(scope, receive, send)
        return

    relative_path = path[len("/static/"):]  
    file_path = STATIC_ROOT / relative_path

    print("Requested path:", path)
    print("Resolved file path:", file_path)
    print("Looking for static file at:", file_path)

    if file_path.exists() and file_path.is_file():
        content_type, _ = guess_type(str(file_path))
        with open(file_path, "rb") as f:
            content = f.read()
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", content_type.encode() if content_type else b"text/plain"),
            ]
        })
        await send({
            "type": "http.response.body",
            "body": content
        })
    else:
        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [(b"content-type", b"text/plain")],
        })
        await send({
            "type": "http.response.body",
            "body": b"Static file not found"
        })

application = ProtocolTypeRouter({
    "http": static_file_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/chats/<int:chat_id>/', ChatConsumer.as_asgi()),
        ])
    )
})
