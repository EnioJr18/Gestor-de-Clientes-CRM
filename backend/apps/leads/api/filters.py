from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter

from apps.leads.models import Lead


class LeadFilter(filters.FilterSet):
    criado_em_de = filters.DateFilter(field_name="criado_em", lookup_expr="date__gte")
    criado_em_ate = filters.DateFilter(field_name="criado_em", lookup_expr="date__lte")

    class Meta:
        model = Lead
        fields = ["status", "prioridade", "criado_em_de", "criado_em_ate"]

    @property
    def qs(self):
        queryset = super().qs
        start = self.form.cleaned_data.get("criado_em_de") if self.form.is_valid() else None
        end = self.form.cleaned_data.get("criado_em_ate") if self.form.is_valid() else None
        if start and end and start > end:
            raise ValidationError({"criado_em_ate": ["A data final deve ser maior ou igual a data inicial."]})
        return queryset


class StrictOrderingFilter(OrderingFilter):
    def remove_invalid_fields(self, queryset, fields, view, request):
        valid_fields = {field for field, _label in self.get_valid_fields(queryset, view, {"request": request})}
        invalid = [field for field in fields if field.lstrip("-") not in valid_fields]
        if invalid:
            raise ValidationError({"ordering": ["Campo de ordenacao nao permitido."]})
        return fields
