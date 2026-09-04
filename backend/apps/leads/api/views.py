from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics

from apps.leads.models import Interaction, Lead

from .filters import LeadFilter, StrictOrderingFilter
from .serializers import InteractionSerializer, LeadSerializer


@extend_schema(auth=[], responses={200: OpenApiResponse(description="API saudavel.")})
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


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


class OwnedLeadInteractionMixin:
    def get_lead(self):
        if not hasattr(self, "_lead"):
            self._lead = get_object_or_404(
                Lead.objects.filter(agente_responsavel=self.request.user),
                pk=self.kwargs["lead_id"],
            )
        return self._lead

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Interaction.objects.none()
        return (
            Interaction.objects.filter(lead=self.get_lead())
            .select_related("lead")
            .order_by("-data_interacao", "-id")
        )


INTERACTION_EXAMPLE = OpenApiExample(
    "Interacao",
    value={
        "id": 1,
        "tipo": "LIGACAO",
        "data_interacao": "2026-09-04T14:30:00-03:00",
        "nota": "Cliente pediu retorno na proxima semana.",
        "criado_em": "2026-09-04T14:31:00-03:00",
        "atualizado_em": "2026-09-04T14:31:00-03:00",
    },
    response_only=True,
)


@extend_schema(
    tags=["Interactions"],
    responses={
        200: InteractionSerializer(many=True),
        401: OpenApiResponse(description="Autenticacao obrigatoria."),
        404: OpenApiResponse(description="Lead inexistente ou fora do escopo do usuario."),
    },
    examples=[INTERACTION_EXAMPLE],
    description="Lista as interacoes do lead autenticado, da mais recente para a mais antiga.",
)
class InteractionListCreateView(OwnedLeadInteractionMixin, generics.ListCreateAPIView):
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Interactions"],
        request=InteractionSerializer,
        responses={
            201: InteractionSerializer,
            400: OpenApiResponse(description="Payload invalido."),
            401: OpenApiResponse(description="Autenticacao obrigatoria."),
            404: OpenApiResponse(description="Lead inexistente ou fora do escopo do usuario."),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(lead=self.get_lead())


@extend_schema(
    tags=["Interactions"],
    responses={
        200: InteractionSerializer,
        401: OpenApiResponse(description="Autenticacao obrigatoria."),
        404: OpenApiResponse(description="Lead ou interacao inexistente, ou fora do escopo do usuario."),
    },
    examples=[INTERACTION_EXAMPLE],
)
class InteractionDetailView(OwnedLeadInteractionMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Interactions"],
        request=InteractionSerializer,
        responses={
            200: InteractionSerializer,
            400: OpenApiResponse(description="Payload invalido."),
            401: OpenApiResponse(description="Autenticacao obrigatoria."),
            404: OpenApiResponse(description="Lead ou interacao inexistente, ou fora do escopo do usuario."),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
