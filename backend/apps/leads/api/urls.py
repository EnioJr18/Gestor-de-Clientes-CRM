from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.api.views import CurrentUserView
from .views import LeadViewSet, health


router = DefaultRouter()
router.register("leads", LeadViewSet, basename="lead")

app_name = "api_v1"

urlpatterns = [
    path("health/", health, name="health"),
    path("users/me/", CurrentUserView.as_view(), name="users_me"),
    path("", include(router.urls)),
]
