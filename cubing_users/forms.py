# cubing_users/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Cuber, Leader, Group
from .constants import (
    COLORS, ADJECTIVES, SUPERHEROES,
    LEADER_ROLES, GROUP_TYPES,
    COLOR_CHOICES
)
from .authentication import hash_color_code, is_color_code_unique
import random
import string

User = get_user_model()


class CuberRegistrationForm(forms.Form):
    """
    Formulaire d'inscription pour les cubeurs.
    Crée une identité unique: Color + Adjective + Superhero + Color Code
    + les 2 premières lettres du prénom et du nom de famille pour identification.
    """
    color = forms.ChoiceField(
        choices=COLORS,
        label="Choisis ta couleur",
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'style': 'font-size: 1.2rem;'
        })
    )

    adjective = forms.ChoiceField(
        choices=ADJECTIVES,
        label="Choisis ton mot de pouvoir",
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'style': 'font-size: 1.2rem;'
        })
    )

    superhero = forms.ChoiceField(
        choices=SUPERHEROES,
        label="Choisis ton titre",
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'style': 'font-size: 1.2rem;'
        })
    )

    # Color code — 6 dropdowns
    color_code_1 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="Position 1")
    color_code_2 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="Position 2")
    color_code_3 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="Position 3")
    color_code_4 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="Position 4")
    color_code_5 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="Position 5")
    color_code_6 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="Position 6")

    # ── Identification ─────────────────────────────────────────────────────
    # Les 2 premières lettres du prénom et du nom de famille.
    # Uniquement visibles par le leader — jamais par les autres élèves.
    # Ex: Tommy Smith → "TO" + "SM" → affiché "TOSM" chez le prof.
    # ──────────────────────────────────────────────────────────────────────
    first_name_prefix = forms.CharField(
        max_length=2,
        label="2 premières lettres de ton prénom",
        help_text="Ex: 'TO' pour Tommy",
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center text-uppercase',
            'placeholder': 'TO',
            'maxlength': '2',
            'autocomplete': 'off',
            'style': 'width: 75px; font-size: 1.3rem; font-weight: 700; letter-spacing: 0.1em;',
        })
    )

    last_name_prefix = forms.CharField(
        max_length=2,
        label="2 premières lettres de ton nom de famille",
        help_text="Ex: 'SM' pour Smith",
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center text-uppercase',
            'placeholder': 'SM',
            'maxlength': '2',
            'autocomplete': 'off',
            'style': 'width: 75px; font-size: 1.3rem; font-weight: 700; letter-spacing: 0.1em;',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 7):
            self.fields[f'color_code_{i}'].widget.attrs.update({
                'class': 'form-select color-code-select',
            })

    def clean_first_name_prefix(self):
        value = self.cleaned_data.get('first_name_prefix', '').strip().upper()
        if len(value) < 1:
            raise ValidationError("Entre au moins 1 lettre de ton prénom.")
        return value[:2]

    def clean_last_name_prefix(self):
        value = self.cleaned_data.get('last_name_prefix', '').strip().upper()
        if len(value) < 1:
            raise ValidationError("Entre au moins 1 lettre de ton nom de famille.")
        return value[:2]

    def clean(self):
        cleaned_data = super().clean()
        color = cleaned_data.get('color')
        adjective = cleaned_data.get('adjective')
        superhero = cleaned_data.get('superhero')

        # Vérifie que l'identité cubeur n'existe pas déjà
        if Cuber.objects.filter(
            color=color,
            adjective=adjective,
            superhero=superhero
        ).exists():
            raise ValidationError(
                "Cette identité existe déjà! Essaie une autre combinaison."
            )

        # Construit et stocke le color_code pour save()
        cleaned_data['color_code'] = [
            cleaned_data.get(f'color_code_{i}')
            for i in range(1, 7)
        ]

        return cleaned_data

    def save(self):
        """Crée et retourne le cubeur"""
        color_code = self.cleaned_data['color_code']

        cuber = Cuber.objects.create(
            color=self.cleaned_data['color'],
            adjective=self.cleaned_data['adjective'],
            superhero=self.cleaned_data['superhero'],
            color_code_hash=hash_color_code(color_code),
            first_name_prefix=self.cleaned_data['first_name_prefix'],
            last_name_prefix=self.cleaned_data['last_name_prefix'],
        )

        return cuber


class CuberLoginForm(forms.Form):
    """
    Formulaire de connexion pour les cubeurs.
    """
    color = forms.ChoiceField(
        choices=COLORS,
        label="Je suis",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    adjective = forms.ChoiceField(
        choices=ADJECTIVES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    superhero = forms.ChoiceField(
        choices=SUPERHEROES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    color_code_1 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="🎨")
    color_code_2 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="🎨")
    color_code_3 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="🎨")
    color_code_4 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="🎨")
    color_code_5 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="🎨")
    color_code_6 = forms.ChoiceField(choices=[(c, c) for c in COLOR_CHOICES], label="🎨")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 7):
            self.fields[f'color_code_{i}'].widget.attrs.update({
                'class': 'form-select form-select-sm color-code-select',
            })

    def get_color_code(self):
        return [
            self.cleaned_data.get(f'color_code_{i}')
            for i in range(1, 7)
        ]


class LeaderRegistrationForm(forms.ModelForm):
    """
    Formulaire d'inscription pour les leaders.
    Crée un compte User standard + profil Leader.
    """
    first_name = forms.CharField(
        max_length=150,
        label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        max_length=150,
        label="Nom de famille",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="Adresse courriel",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Au moins 8 caractères"
    )

    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Leader
        fields = ['role', 'organization']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'École, club, organisation (optionnel)'
            })
        }
        labels = {
            'role': 'Votre rôle',
            'organization': 'Organisation (optionnel)'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse courriel est déjà utilisée.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Les mots de passe ne correspondent pas.")

        if password1 and len(password1) < 8:
            raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")

        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        leader = Leader.objects.create(
            user=user,
            role=self.cleaned_data['role'],
            organization=self.cleaned_data.get('organization', '')
        )
        return leader


class LeaderLoginForm(forms.Form):
    """
    Formulaire de connexion pour les leaders (auth standard).
    """
    email = forms.EmailField(
        label="Adresse courriel",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre@courriel.com'
        })
    )

    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class GroupCreationForm(forms.ModelForm):
    """
    Formulaire de création de groupe (classe/club).
    """
    class Meta:
        model = Group
        fields = ['group_name', 'group_type']
        widgets = {
            'group_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Classe de 4e année'
            }),
            'group_type': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'group_name': 'Nom du groupe',
            'group_type': 'Type de groupe',
        }

    def save(self, commit=True):
        group = super().save(commit=False)
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Group.objects.filter(group_code=code).exists():
                group.group_code = code
                break
        if commit:
            group.save()
        return group


class JoinGroupForm(forms.Form):
    """
    Formulaire pour rejoindre un groupe avec un code.
    """
    group_code = forms.CharField(
        max_length=6,
        label="Code du groupe",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': 'CUBE42',
            'style': 'letter-spacing: 0.3em; text-transform: uppercase;'
        }),
        help_text="Entre le code à 6 caractères donné par ton enseignant(e)"
    )

    def clean_group_code(self):
        code = self.cleaned_data.get('group_code', '').upper().strip()
        try:
            Group.objects.get(group_code=code)
        except Group.DoesNotExist:
            raise ValidationError("Ce code de groupe n'existe pas. Vérifie le code et réessaie.")
        return code

    def get_group(self):
        return Group.objects.get(group_code=self.cleaned_data.get('group_code'))