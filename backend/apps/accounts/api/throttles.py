from rest_framework.throttling import SimpleRateThrottle


class IpScopedThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class LoginRateThrottle(IpScopedThrottle):
    scope = "auth_login"


class RefreshRateThrottle(IpScopedThrottle):
    scope = "auth_refresh"


class CsrfRateThrottle(IpScopedThrottle):
    scope = "auth_csrf"
