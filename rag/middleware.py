from urllib.parse import parse_qs


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser
        from rest_framework.authtoken.models import Token

        qs = scope.get("query_string", b"").decode()
        params = parse_qs(qs)
        token_keys = params.get("token")
        if token_keys:
            try:
                token = Token.objects.get(key=token_keys[0])
                scope["user"] = token.user
            except Token.DoesNotExist:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()
        return await self.inner(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)
