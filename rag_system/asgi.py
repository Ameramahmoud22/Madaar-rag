"""
ASGI config for rag_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import rag.routing
from rag.middleware import TokenAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import os
import django
from django.core.asgi import get_asgi_application

# This is the crucial part: Set the settings module and then explicitly run django.setup()
# This configures Django's settings and makes them available everywhere.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rag_system.settings')
django.setup()

# Now that Django is set up, we can safely import our other modules.


application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests.
    "http": get_asgi_application(),

    # WebSocket handler
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            rag.routing.websocket_urlpatterns
        )
    ),
})
