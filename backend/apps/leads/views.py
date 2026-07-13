from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views import generic
from django.db.models import Count
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
import csv

from .models import Lead, Interaction
from .forms import InteractionForm, UserProfileForm, LeadForm


CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _sanitize_csv_cell(value):
    if value is None:
        return ""

    text = str(value)
    if text.startswith("'"):
        return text
    if text.startswith(CSV_FORMULA_PREFIXES):
        return f"'{text}"
    return text


def _sanitize_csv_row(values):
    return [_sanitize_csv_cell(value) for value in values]


def _choice_value(choices, raw_value):
    for value, display in choices:
        if raw_value.lower() in {value.lower(), display.lower()}:
            return value
    return None



@login_required
def dashboard(request):
    # Otimização: Filtramos uma vez só o queryset base
    leads_usuario = Lead.objects.filter(agente_responsavel=request.user)
    
    total_leads = leads_usuario.count()
    novos_hoje = leads_usuario.filter(criado_em__date=timezone.localdate()).count()
    
    # 1. Gráfico de Status
    status_data = leads_usuario.values('status').annotate(total=Count('status'))
    labels_status = [item['status'] for item in status_data]
    data_status = [item['total'] for item in status_data]

    # 2. Gráfico de Prioridade
    prioridade_data = leads_usuario.values('prioridade').annotate(total=Count('prioridade'))
    labels_prioridade = [item['prioridade'] for item in prioridade_data]
    data_prioridade = [item['total'] for item in prioridade_data]
    
    # Interações recentes (apenas do usuário)
    interacoes_recentes = Interaction.objects.filter(
        lead__agente_responsavel=request.user
    ).select_related('lead').order_by('-data_interacao')[:5]

    contexto = {
        'total_leads': total_leads,
        'labels_status': labels_status,
        'data_status': data_status,
        'labels_prioridade': labels_prioridade,
        'data_prioridade': data_prioridade,
        'interacoes_recentes': interacoes_recentes,
        'novos_hoje': novos_hoje,
    }
    return render(request, 'leads/dashboard.html', contexto)

class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"
    paginate_by = 10

    def get_queryset(self):
        qs = Lead.objects.filter(agente_responsavel=self.request.user).order_by('-criado_em')
        
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(nome__icontains=query)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class LeadCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadForm
    success_url = reverse_lazy("leads:lead_list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.agente_responsavel = self.request.user
        lead.save()
        messages.success(self.request, "Lead criado com sucesso!")
        return super().form_valid(form)

class LeadUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadForm
    
    def get_queryset(self):
        return Lead.objects.filter(agente_responsavel=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Lead atualizado!")
        return reverse("leads:lead_list")

class LeadDeleteView(LoginRequiredMixin, generic.DeleteView): 
    
    def get_queryset(self):
        return Lead.objects.filter(agente_responsavel=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Lead excluído com sucesso.")
        return reverse("leads:lead_list")


@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk, agente_responsavel=request.user)
    interacoes = Interaction.objects.filter(lead=lead).order_by('-data_interacao')
    
    form = InteractionForm()
    
    if request.method == 'POST':
        form = InteractionForm(request.POST)
        if form.is_valid():
            interacao = form.save(commit=False)
            interacao.lead = lead
            interacao.save()
            messages.success(request, "Anotação registrada!")
            return redirect('leads:lead_detail', pk=lead.pk)

    contexto = {
        'lead': lead,
        'interacoes': interacoes,
        'form': form,
    }
    return render(request, 'leads/lead_detail.html', contexto)

@login_required
def interaction_delete(request, pk):
    interacao = get_object_or_404(Interaction, pk=pk, lead__agente_responsavel=request.user)
    lead_pk = interacao.lead.pk
    
    if request.method == 'POST':
        interacao.delete()
        messages.success(request, "Interação removida.")
        return redirect('leads:lead_detail', pk=lead_pk)
    
    return redirect('leads:lead_detail', pk=lead_pk)

@login_required
def interaction_update(request, pk):
    interacao = get_object_or_404(Interaction, pk=pk, lead__agente_responsavel=request.user)
    form = InteractionForm(request.POST or None, instance=interacao)
    
    if form.is_valid():
        form.save()
        messages.success(request, "Interação atualizada.")
        return redirect('leads:lead_detail', pk=interacao.lead.pk)
    
    return render(request, 'leads/interaction_update.html', {'form': form, 'interacao': interacao})


@login_required
def leads_by_status(request, status):
    leads = Lead.objects.filter(status=status, agente_responsavel=request.user).order_by('-criado_em')
    return render(request, 'leads/lead_list.html', {'leads': leads, 'filtro': f'Status: {status}'})

@login_required
def leads_by_priority(request, prioridade):
    prioridade_value = _choice_value(Lead.PRIORITY_CHOICES, prioridade)
    leads = Lead.objects.none()
    if prioridade_value:
        leads = Lead.objects.filter(prioridade=prioridade_value, agente_responsavel=request.user).order_by('-criado_em')
    return render(request, 'leads/lead_list.html', {'leads': leads, 'filtro': f'Prioridade: {prioridade}'})

@login_required
def recent_leads(request):
    leads = Lead.objects.filter(agente_responsavel=request.user).order_by('-criado_em')[:10]
    return render(request, 'leads/lead_list.html', {'leads': leads, 'filtro': 'Leads Recentes'})

@login_required
def high_priority_leads(request):
    prioridade_value = _choice_value(Lead.PRIORITY_CHOICES, 'Alta')
    leads = Lead.objects.filter(prioridade=prioridade_value, agente_responsavel=request.user).order_by('-criado_em')
    return render(request, 'leads/lead_list.html', {'leads': leads, 'filtro': 'Leads de Alta Prioridade'})

@login_required
def leads_without_interactions(request):
    leads = Lead.objects.filter(agente_responsavel=request.user).annotate(num_interactions=Count('interactions')).filter(num_interactions=0)
    return render(request, 'leads/lead_list.html', {'leads': leads, 'filtro': 'Leads sem Interações'})



@login_required
def export_leads_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leads.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nome', 'Email', 'Telefone', 'Status', 'Prioridade', 'Criado Em'])


    leads = Lead.objects.filter(agente_responsavel=request.user).values_list(
        'nome', 'email', 'telefone', 'status', 'prioridade', 'criado_em'
    )
    for lead in leads:
        writer.writerow(_sanitize_csv_row(lead))

    return response


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('leads:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'leads/profile.html', {'form': form})

@login_required# leads/views.py

# ... (código anterior)

@login_required
def export_interactions_csv(request, lead_id):
    # Busca o lead garantindo que pertence ao usuário logado
    lead = get_object_or_404(Lead, pk=lead_id, agente_responsavel=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="historico_{lead.nome}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Data', 'Nota']) 

    interacoes = Interaction.objects.filter(lead=lead).order_by('-data_interacao')
    
    for interacao in interacoes:
        writer.writerow([
            interacao.data_interacao.strftime("%d/%m/%Y %H:%M"), 
            _sanitize_csv_cell(interacao.nota)
        ])

    return response
