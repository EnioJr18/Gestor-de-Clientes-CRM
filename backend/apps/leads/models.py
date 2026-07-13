from django.db import models
from django.contrib.auth.models import User

class Lead(models.Model):
    STATUS_CHOICES = (
        ('NOVO', 'Novo'),
        ('EM_NEGOCIACAO', 'Em Negociação'), 
        ('PROPOSTA_ENVIADA', 'Proposta Enviada'),
        ('VENDIDO', 'Vendido'),
        ('PERDIDO', 'Perdido'),
    )
    
    PRIORITY_CHOICES = (
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'), 
        ('ALTA', 'Alta'),
    )

    
    nome = models.CharField(max_length=255, verbose_name='Nome do Cliente')
    sobrenome = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOVO')
    prioridade = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIA')

    agente_responsavel = models.ForeignKey(
        User, 
        related_name='leads', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} - {self.get_status_display()}"


class Interaction(models.Model):
    """
    Registra cada contato feito com o cliente.
    """
    lead = models.ForeignKey(Lead, related_name='interactions', on_delete=models.CASCADE)

    nota = models.TextField(verbose_name='Anotações')
    data_interacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interação em {self.data_interacao} com {self.lead.nome}"