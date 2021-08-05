from channels.routing import (ProtocolTypeRouter, URLRouter)
from channels.auth import AuthMiddlewareStack
from data_handler.routing import websocket_url_pattern

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_url_pattern
        )
    )
})
