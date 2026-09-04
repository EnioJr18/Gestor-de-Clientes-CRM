from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


STATUS_NOVO = "NOVO"
STATUS_EM_NEGOCIACAO = "EM_NEGOCIACAO"
STATUS_PROPOSTA_ENVIADA = "PROPOSTA_ENVIADA"
STATUS_VENDIDO = "VENDIDO"
STATUS_PERDIDO = "PERDIDO"

STATUS_CHOICES = (
    (STATUS_NOVO, "Novo"),
    (STATUS_EM_NEGOCIACAO, "Em Negocia\u00e7\u00e3o"),
    (STATUS_PROPOSTA_ENVIADA, "Proposta Enviada"),
    (STATUS_VENDIDO, "Vendido"),
    (STATUS_PERDIDO, "Perdido"),
)
STATUS_VALUES = [value for value, _label in STATUS_CHOICES]

PRIORITY_BAIXA = "BAIXA"
PRIORITY_MEDIA = "MEDIA"
PRIORITY_ALTA = "ALTA"

PRIORITY_CHOICES = (
    (PRIORITY_BAIXA, "Baixa"),
    (PRIORITY_MEDIA, "M\u00e9dia"),
    (PRIORITY_ALTA, "Alta"),
)
PRIORITY_VALUES = [value for value, _label in PRIORITY_CHOICES]

INTERACTION_TIPO_LIGACAO = "LIGACAO"
INTERACTION_TIPO_EMAIL = "EMAIL"
INTERACTION_TIPO_REUNIAO = "REUNIAO"
INTERACTION_TIPO_MENSAGEM = "MENSAGEM"
INTERACTION_TIPO_NOTA = "NOTA"

INTERACTION_TIPO_CHOICES = (
    (INTERACTION_TIPO_LIGACAO, "Ligacao"),
    (INTERACTION_TIPO_EMAIL, "E-mail"),
    (INTERACTION_TIPO_REUNIAO, "Reuniao"),
    (INTERACTION_TIPO_MENSAGEM, "Mensagem"),
    (INTERACTION_TIPO_NOTA, "Nota"),
)
INTERACTION_TIPO_VALUES = [value for value, _label in INTERACTION_TIPO_CHOICES]


class Lead(models.Model):
    STATUS_NOVO = STATUS_NOVO
    STATUS_EM_NEGOCIACAO = STATUS_EM_NEGOCIACAO
    STATUS_PROPOSTA_ENVIADA = STATUS_PROPOSTA_ENVIADA
    STATUS_VENDIDO = STATUS_VENDIDO
    STATUS_PERDIDO = STATUS_PERDIDO
    STATUS_CHOICES = STATUS_CHOICES
    STATUS_VALUES = STATUS_VALUES

    PRIORITY_BAIXA = PRIORITY_BAIXA
    PRIORITY_MEDIA = PRIORITY_MEDIA
    PRIORITY_ALTA = PRIORITY_ALTA
    PRIORITY_CHOICES = PRIORITY_CHOICES
    PRIORITY_VALUES = PRIORITY_VALUES

    nome = models.CharField(max_length=255, verbose_name="Nome do Cliente")
    sobrenome = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOVO)
    prioridade = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIA)

    agente_responsavel = models.ForeignKey(
        User,
        related_name="leads",
        on_delete=models.CASCADE,
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                "agente_responsavel",
                Lower("email"),
                name="lead_owner_email_ci_uniq",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=STATUS_VALUES),
                name="lead_status_valid_chk",
            ),
            models.CheckConstraint(
                condition=models.Q(prioridade__in=PRIORITY_VALUES),
                name="lead_priority_valid_chk",
            ),
            models.CheckConstraint(
                condition=~models.Q(nome=""),
                name="lead_nome_not_empty_chk",
            ),
            models.CheckConstraint(
                condition=~models.Q(email=""),
                name="lead_email_not_empty_chk",
            ),
        ]
        indexes = [
            models.Index(fields=["agente_responsavel", "status"], name="lead_owner_status_idx"),
            models.Index(fields=["agente_responsavel", "prioridade"], name="lead_owner_priority_idx"),
            models.Index(fields=["agente_responsavel", "-criado_em"], name="lead_owner_created_idx"),
        ]

    def __str__(self):
        return f"{self.nome} - {self.get_status_display()}"


class Interaction(models.Model):
    """Registra cada contato feito com o cliente."""

    TIPO_LIGACAO = INTERACTION_TIPO_LIGACAO
    TIPO_EMAIL = INTERACTION_TIPO_EMAIL
    TIPO_REUNIAO = INTERACTION_TIPO_REUNIAO
    TIPO_MENSAGEM = INTERACTION_TIPO_MENSAGEM
    TIPO_NOTA = INTERACTION_TIPO_NOTA
    TIPO_CHOICES = INTERACTION_TIPO_CHOICES

    lead = models.ForeignKey(Lead, related_name="interactions", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=INTERACTION_TIPO_CHOICES, default=INTERACTION_TIPO_NOTA)
    nota = models.TextField(verbose_name="Anota\u00e7\u00f5es")
    data_interacao = models.DateTimeField(default=timezone.now)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(tipo__in=INTERACTION_TIPO_VALUES),
                name="interaction_tipo_valid_chk",
            ),
            models.CheckConstraint(
                condition=~models.Q(nota=""),
                name="interaction_nota_not_empty_chk",
            ),
        ]
        indexes = [
            models.Index(fields=["lead", "-data_interacao"], name="inter_lead_date_idx"),
        ]

    def __str__(self):
        return f"Intera\u00e7\u00e3o em {self.data_interacao} com {self.lead.nome}"

    def clean(self):
        super().clean()
        if self.nota is not None and not self.nota.strip():
            raise ValidationError({"nota": "Informe uma anotacao."})
