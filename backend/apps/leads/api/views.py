from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.leads.models import Lead

from .filters import LeadFilter, StrictOrderingFilter
from .serializers import CurrentUserSerializer, LeadSerializer


@extend_schema(auth=[], responses={200: OpenApiResponse(description="API saudavel.")})
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CurrentUserSerializer)
    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)


class LeadViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = LeadFilter
    search_fields = ["nome", "sobrenome", "email", "telefone"]
    ordering_fields = ["nome", "email", "status", "prioridade", "criado_em", "atualizado_em"]
    ordering = ["-criado_em"]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        StrictOrderingFilter,
    ]
    allowed_query_params = {
        "page",
        "page_size",
        "search",
        "ordering",
        "status",
        "prioridade",
        "criado_em_de",
        "criado_em_ate",
    }

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Lead.objects.none()
        return Lead.objects.filter(agente_responsavel=self.request.user).order_by("-criado_em")

    def filter_queryset(self, queryset):
        unknown = set(self.request.query_params) - self.allowed_query_params
        if unknown:
            raise ValidationError({field: ["Parametro desconhecido."] for field in sorted(unknown)})
        return super().filter_queryset(queryset)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        return get_object_or_404(queryset, pk=self.kwargs[self.lookup_url_kwarg or self.lookup_field])

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError as exc:
            raise ValidationError(
                {"email": ["Ja existe um lead com este e-mail para este usuario."]}
            ) from exc
