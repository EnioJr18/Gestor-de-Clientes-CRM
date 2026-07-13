from django.contrib import admin
from .models import Lead, Interaction

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'status', 'prioridade', 'agente_responsavel', 'criado_em')
    list_filter = ('status', 'prioridade', 'criado_em', 'agente_responsavel')
    search_fields = ('nome', 'email', 'telefone')
    ordering = ('-criado_em',)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('lead', 'data_interacao')
    search_fields = ('lead__nome', 'nota')
    ordering = ('-data_interacao',)

