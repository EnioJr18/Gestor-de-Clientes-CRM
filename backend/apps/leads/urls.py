from django.urls import path
from .views import dashboard, lead_detail, interaction_delete, LeadListView, LeadCreateView, LeadUpdateView, LeadDeleteView, interaction_update
from apps.leads import views
from . import views

app_name = 'leads'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('criar/', LeadCreateView.as_view(), name='lead_create'),
    path('<int:pk>/', lead_detail, name='lead_detail'),
    path('lista/', LeadListView.as_view(), name='lead_list'),
    path('<int:pk>/editar/', LeadUpdateView.as_view(), name='lead_update'),
    path('<int:pk>/deletar/', LeadDeleteView.as_view(), name='lead_delete'),
    path('cadastro/', views.signup_view, name='signup'),
    # Interações
    path('interacao/<int:pk>/editar/', views.interaction_update, name='interaction_update'),
    path('interacao/<int:pk>/deletar/', views.interaction_delete, name='interaction_delete'),
    path('configuracoes/', views.profile_view, name='profile'),
    
    # Busca e Filtros
    path('recentes/', views.recent_leads, name='recent_leads'),
    path('sem-interacao/', views.leads_without_interactions, name='leads_without_interactions'),
    path('prioridade-alta/', views.high_priority_leads, name='high_priority_leads'),
    
    # Exportação
    path('exportar/csv/', views.export_leads_csv, name='export_leads_csv'),
    path('exportar/interacoes/<int:lead_id>/csv/', views.export_interactions_csv, name='export_interactions_csv'),
]
