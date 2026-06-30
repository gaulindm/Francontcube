# cubing_users/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import (
    Cuber, Leader, Group,
    ANIMAL_CHOICES, CUBE_COLOR_CHOICES, QUALITY_CHOICES,
)
from .authentication import hash_color_code
import random
import string

User = get_user_model()

# Choix valides pour le code secret (les 6 couleurs du cube, en français)
COLOR_CODE_CHOICES = [
    ('Rouge',  'Rouge'),
    ('Orange', 'Orange'),
    ('Jaune',  'Jaune'),
    ('Vert',   'Vert'),
    ('Bleu',   'Bleu'),
    ('Blanc',  'Blanc'),
]


class CuberRegistrationForm(forms.Form):
    """
    Formulaire d'inscription pour les cubeurs.

    Identité visuelle (choisie dans le wizard JS) :
      • animal      — 1 parmi 12
      • cube_color  — couleur du foulard, 1 parmi 6
      • quality_1   — première qualité, 1 parmi 15
      • quality_2   — deuxième qualité, 1 parmi 15 (différente de quality_1)

    Code secret — 6 couleurs dans l'ordre (mot de passe visuel)

    Identification leader-only :
      • first_name_prefix — 2 premières lettres du prénom
      • last_name_prefix  — 2 premières lettres du nom de famille
    """

    # ── Identité visuelle ──────────────────────────────────────────────────
    animal = forms.ChoiceField(
        choices=ANIMAL_CHOICES,
        label="Ton animal",
        widget=forms.HiddenInput(),
    )
    cube_color = forms.ChoiceField(
        choices=CUBE_COLOR_CHOICES,
        label="Couleur du foulard",
        widget=forms.HiddenInput(),
    )
    quality_1 = forms.ChoiceField(
        choices=QUALITY_CHOICES,
        label="Première qualité",
        widget=forms.HiddenInput(),
    )
    quality_2 = forms.ChoiceField(
        choices=QUALITY_CHOICES,
        label="Deuxième qualité",
        widget=forms.HiddenInput(),
    )

    # ── Code secret — 6 positions ──────────────────────────────────────────
    color_code_1 = forms.ChoiceField(choices=COLOR_CODE_CHOICES, label="Position 1", widget=forms.HiddenInput())
    color_code_2 = forms.ChoiceField(choices=COLOR_CODE_CHOICES, label="Position 2", widget=forms.HiddenInput())
    color_code_3 = forms.ChoiceField(choices=COLOR_CODE_CHOICES, label="Position 3", widget=forms.HiddenInput())

    # ── Identification leader-only ─────────────────────────────────────────
    first_name_prefix = forms.CharField(
        max_length=2,
        label="2 premières lettres du prénom",
        help_text="Ex: 'TO' pour Tommy",
        widget=forms.HiddenInput(),
    )
    last_name_prefix = forms.CharField(
        max_length=2,
        label="2 premières lettres du nom de famille",
        help_text="Ex: 'SM' pour Smith",
        widget=forms.HiddenInput(),
    )

    # ── Validation ─────────────────────────────────────────────────────────

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
        animal     = cleaned_data.get('animal')
        cube_color = cleaned_data.get('cube_color')
        quality_1  = cleaned_data.get('quality_1')
        quality_2  = cleaned_data.get('quality_2')

        # Les deux qualités doivent être différentes
        if quality_1 and quality_2 and quality_1 == quality_2:
            raise ValidationError("Choisis deux qualités différentes!")

        # Vérifie que la combinaison animal + couleur + qualités n'existe pas déjà
        if animal and cube_color and quality_1 and quality_2:
            if Cuber.objects.filter(
                animal=animal,
                cube_color=cube_color,
                quality_1=quality_1,
                quality_2=quality_2,
            ).exists():
                raise ValidationError(
                    "Cette combinaison existe déjà! Essaie de changer une qualité ou ta couleur."
                )

        # Assemble le code secret pour save()
        cleaned_data['color_code'] = [
            cleaned_data.get(f'color_code_{i}')
            for i in range(1, 4)
        ]

        return cleaned_data

    def save(self):
        """Crée et retourne le cubeur."""
        cd = self.cleaned_data
        cuber = Cuber(
            animal=cd['animal'],
            cube_color=cd['cube_color'],
            quality_1=cd['quality_1'],
            quality_2=cd['quality_2'],
            first_name_prefix=cd['first_name_prefix'],
            last_name_prefix=cd['last_name_prefix'],
        )
        cuber.set_color_code(','.join(cd['color_code']))
        cuber.save()
        return cuber


class CuberLoginForm(forms.Form):
    """
    Formulaire de connexion pour les cubeurs.
    L'identité est vérifiée via animal + cube_color + quality_1 + quality_2
    et le code secret (6 couleurs hashées).
    """

    animal = forms.ChoiceField(
        choices=ANIMAL_CHOICES,
        label="Ton animal",
        widget=forms.HiddenInput(),
    )
    cube_color = forms.ChoiceField(
        choices=CUBE_COLOR_CHOICES,
        label="Couleur du foulard",
        widget=forms.HiddenInput(),
    )
    quality_1 = forms.ChoiceField(
        choices=QUALITY_CHOICES,
        label="Première qualité",
        widget=forms.HiddenInput(),
    )
    quality_2 = forms.ChoiceField(
        choices=QUALITY_CHOICES,
        label="Deuxième qualité",
        widget=forms.HiddenInput(),
    )

    color_code_1 = forms.ChoiceField(choices=COLOR_CODE_CHOICES, label="🎨", widget=forms.HiddenInput())
    color_code_2 = forms.ChoiceField(choices=COLOR_CODE_CHOICES, label="🎨", widget=forms.HiddenInput())
    color_code_3 = forms.ChoiceField(choices=COLOR_CODE_CHOICES, label="🎨", widget=forms.HiddenInput())

    def get_color_code(self):
        """Retourne la liste des 6 couleurs du code secret."""
        return [
            self.cleaned_data.get(f'color_code_{i}')
            for i in range(1, 4)
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
            last_name=self.cleaned_data['last_name'],
        )
        leader = Leader.objects.create(
            user=user,
            role=self.cleaned_data['role'],
            organization=self.cleaned_data.get('organization', '')
        )
        return leader


class LeaderLoginForm(forms.Form):
    """Formulaire de connexion pour les leaders (auth standard Django)."""
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
    """Formulaire de création de groupe (classe/club)."""
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
    """Formulaire pour rejoindre un groupe avec un code."""
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
