from django import forms
from django.contrib.auth.models import User

from .models import Interaction, Lead


class LeadForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        owner = self.user or getattr(self.instance, "agente_responsavel", None)
        if owner is not None:
            duplicates = Lead.objects.filter(agente_responsavel=owner, email__iexact=email)
            if self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                raise forms.ValidationError("Ja existe um lead com este e-mail para este usuario.")
        return email

    class Meta:
        model = Lead
        fields = ["nome", "sobrenome", "email", "telefone", "status", "prioridade"]

        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Jo\u00e3o"}),
            "sobrenome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Silva"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "joao@empresa.com"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "prioridade": forms.Select(attrs={"class": "form-select"}),
        }


class InteractionForm(forms.ModelForm):
    def clean_nota(self):
        nota = self.cleaned_data["nota"].strip()
        if not nota:
            raise forms.ValidationError("Informe uma anotacao.")
        return nota

    class Meta:
        model = Interaction
        fields = ["nota"]
        widgets = {
            "nota": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descreva o que foi conversado...",
                }
            )
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
