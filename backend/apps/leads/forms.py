from django import forms
from .models import Lead, Interaction
from django.contrib.auth.models import User

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['nome', 'sobrenome', 'email', 'telefone', 'status', 'prioridade']

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João'}),
            'sobrenome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Silva'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'joao@empresa.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),     
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
        }

class InteractionForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = ['nota']
        widgets = {
            'nota': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Descreva o que foi conversado...'
            })
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }