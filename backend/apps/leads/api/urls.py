from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.api.views import CurrentUserView
from .dashboard import dashboard_summary
from .views import InteractionDetailView, InteractionListCreateView, LeadViewSet, health


router = DefaultRouter()
router.register("leads", LeadViewSet, basename="lead")

app_name = "api_v1"

urlpatterns = [
    path("health/", health, name="health"),
    path("users/me/", CurrentUserView.as_view(), name="users_me"),
    path("dashboard/summary/", dashboard_summary, name="dashboard-summary"),
    path(
        "leads/<int:lead_id>/interactions/",
        InteractionListCreateView.as_view(),
        name="interaction-list",
    ),
    path(
        "leads/<int:lead_id>/interactions/<int:pk>/",
        InteractionDetailView.as_view(),
        name="interaction-detail",
    ),
    path("", include(router.urls)),
]
