from datetime import date, timedelta

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.leads.models import Lead
from .serializers import DashboardSummarySerializer


PERIOD_DAYS = {"7d": 7, "30d": 30, "90d": 90}
MAX_CUSTOM_DAYS = 366


def _period(query):
    key = query.get("period", "30d")
    today = timezone.localdate()
    if key == "custom":
        date_from = query.get("date_from")
        date_to = query.get("date_to")
        missing = {}
        if not date_from:
            missing["date_from"] = ["Este campo e obrigatorio para periodo custom."]
        if not date_to:
            missing["date_to"] = ["Este campo e obrigatorio para periodo custom."]
        if missing:
            raise ValidationError(missing)
        try:
            start = date.fromisoformat(date_from)
            end = date.fromisoformat(date_to)
        except ValueError as exc:
            raise ValidationError({"date_from": ["Datas devem usar YYYY-MM-DD."]}) from exc
        if start > end:
            raise ValidationError({"date_to": ["A data final deve ser maior ou igual a inicial."]})
        if (end - start).days > MAX_CUSTOM_DAYS:
            raise ValidationError({"date_to": ["O periodo personalizado suporta no maximo 366 dias."]})
        return key, start, end
    if key == "12m":
        start = today.replace(day=1)
        for _ in range(11):
            start = (start - timedelta(days=1)).replace(day=1)
        return key, start, today
    if key not in PERIOD_DAYS:
        raise ValidationError({"period": ["Periodo nao permitido."]})
    return key, today - timedelta(days=PERIOD_DAYS[key] - 1), today


def _months(start, end, counts):
    labels = ("Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez")
    current = start.replace(day=1)
    last = end.replace(day=1)
    result = []
    while current <= last:
        month = current.strftime("%Y-%m")
        result.append({"month": month, "label": f"{labels[current.month - 1]}/{current.year}", "count": counts.get(month, 0)})
        current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
    return result


@extend_schema(
    parameters=[
        OpenApiParameter("period", str, description="7d, 30d, 90d, 12m ou custom."),
        OpenApiParameter("date_from", str, description="YYYY-MM-DD, obrigatoria em custom."),
        OpenApiParameter("date_to", str, description="YYYY-MM-DD, obrigatoria em custom."),
    ],
    responses={
        200: DashboardSummarySerializer,
        400: OpenApiResponse(description="Periodo invalido."),
        401: OpenApiResponse(description="Autenticacao obrigatoria."),
        403: OpenApiResponse(description="Requisicao autenticada sem permissao."),
        429: OpenApiResponse(description="Limite de requisicoes excedido."),
    },
    examples=[
        OpenApiExample(
            "Resumo de 30 dias",
            value={
                "period": {"key": "30d", "date_from": "2026-06-16", "date_to": "2026-07-15"},
                "metrics": {"total_leads": 12, "created_today": 1, "created_in_period": 7, "converted_in_period": 2, "conversion_rate": 28.6},
                "by_status": [{"status": "NOVO", "label": "Novo", "count": 3}],
                "by_priority": [{"priority": "ALTA", "label": "Alta", "count": 2}],
                "monthly_evolution": [{"month": "2026-07", "label": "Jul/2026", "count": 4}],
                "recent_leads": [],
            },
            response_only=True,
            status_codes=["200"],
        )
    ],
    description=(
        "Metricas de leads do usuario autenticado. Todos os valores sao isolados por "
        "agente_responsavel; nao ha dados de outros usuarios. O periodo custom exige "
        "date_from e date_to inclusivos em YYYY-MM-DD."
    ),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    key, start, end = _period(request.query_params)
    leads = Lead.objects.filter(agente_responsavel=request.user)
    period_leads = leads.filter(criado_em__date__range=(start, end))
    created = period_leads.count()
    converted = period_leads.filter(status=Lead.STATUS_VENDIDO).count()
    status_counts = {row["status"]: row["count"] for row in leads.values("status").annotate(count=Count("id"))}
    priority_counts = {row["prioridade"]: row["count"] for row in leads.values("prioridade").annotate(count=Count("id"))}
    months = leads.filter(criado_em__date__range=(start, end)).annotate(month=TruncMonth("criado_em")).values("month").annotate(count=Count("id")).order_by("month")
    monthly = _months(start, end, {row["month"].strftime("%Y-%m"): row["count"] for row in months})
    recent = list(leads.order_by("-criado_em", "-id").values("id", "nome", "sobrenome", "email", "status", "prioridade", "criado_em")[:5])
    payload = {
        "period": {"key": key, "date_from": start, "date_to": end},
        "metrics": {"total_leads": leads.count(), "created_today": leads.filter(criado_em__date=timezone.localdate()).count(), "created_in_period": created, "converted_in_period": converted, "conversion_rate": round(converted / created * 100, 1) if created else 0.0},
        "by_status": [{"status": value, "label": label, "count": status_counts.get(value, 0)} for value, label in Lead.STATUS_CHOICES],
        "by_priority": [{"priority": value, "label": label, "count": priority_counts.get(value, 0)} for value, label in Lead.PRIORITY_CHOICES],
        "monthly_evolution": monthly,
        "recent_leads": recent,
    }
    return Response(DashboardSummarySerializer(payload).data)
