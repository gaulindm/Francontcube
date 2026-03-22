# cubing_users/models.py
import uuid
import hashlib
from django.db import models
from django.conf import settings
from django.utils import timezone


class Cuber(models.Model):
    """Utilisateur cubeur anonyme (enfants)"""
    cuber_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    color = models.CharField(max_length=10)
    adjective = models.CharField(max_length=50)
    superhero = models.CharField(max_length=50)
    color_code_hash = models.CharField(max_length=128)
    created_date = models.DateTimeField(auto_now_add=True)
    last_active_date = models.DateTimeField(auto_now=True)

    # ✅ Lien OPTIONNEL vers compte traditionnel
    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuber_profiles'
    )

    # ── Identification saisie à la création du compte ──────────────────────
    # L'élève entre les 2 premières lettres de son prénom et de son nom de
    # famille lors de l'inscription. Ex: Tommy Smith → "TO" + "SM" → "TOSM".
    # Ces valeurs sont copiées dans GroupMembership à chaque fois que l'élève
    # rejoint un groupe. Le leader peut les corriger par groupe si nécessaire.
    # ──────────────────────────────────────────────────────────────────────
    first_name_prefix = models.CharField(
        max_length=2,
        blank=True,
        help_text="2 premières lettres du prénom (ex: 'TO' pour Tommy)"
    )
    last_name_prefix = models.CharField(
        max_length=2,
        blank=True,
        help_text="2 premières lettres du nom de famille (ex: 'SM' pour Smith)"
    )

    def __str__(self):
        return f"{self.color} {self.adjective} {self.superhero}"

    def save(self, *args, **kwargs):
        # Normalize prefixes: uppercase, strip whitespace, hard-cap at 2 chars
        self.first_name_prefix = self.first_name_prefix.strip().upper()[:2]
        self.last_name_prefix = self.last_name_prefix.strip().upper()[:2]
        super().save(*args, **kwargs)

    def set_color_code(self, plain_color_code: str):
        """
        Hash and store a new color code.
        Call save() after this method to persist the change.

        Usage:
            cuber.set_color_code("rouge-bleu-vert")
            cuber.save()
        """
        self.color_code_hash = hashlib.sha256(plain_color_code.encode()).hexdigest()


class Leader(models.Model):
    """Leader (prof/coach) - utilise auth traditionnelle"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leader_profile'
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('teacher', 'Enseignant'),
            ('coach', 'Entraîneur'),
            ('club_leader', 'Animateur de Club'),
            ('parent', 'Parent Responsable'),
        ]
    )
    organization = models.CharField(max_length=200, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"


class Group(models.Model):
    """Classe ou club de cubing"""
    group_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    group_name = models.CharField(max_length=200)
    group_code = models.CharField(max_length=6, unique=True)
    group_type = models.CharField(
        max_length=20,
        choices=[
            ('class', 'Classe'),
            ('club', 'Club'),
            ('team', 'Équipe'),
            ('practice', 'Groupe de Pratique'),
        ]
    )
    leaders = models.ManyToManyField(Leader, related_name='groups')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group_name


class GroupMembership(models.Model):
    """Relation N-to-N Cuber ↔ Group"""
    cuber = models.ForeignKey(Cuber, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Actif'),
            ('inactive', 'Inactif'),
        ],
        default='active'
    )

    # ── Leader-only identification ─────────────────────────────────────────
    # Seeded from Cuber.first_name_prefix / last_name_prefix when the student
    # joins the group. The leader can correct them per-group if needed.
    # Displayed as "TOSM" (Tommy Smith) — never shown to the student.
    # ──────────────────────────────────────────────────────────────────────
    first_name_prefix = models.CharField(
        max_length=2,
        blank=True,
        help_text="2 premières lettres du prénom (ex: 'TO' pour Tommy)"
    )
    last_name_prefix = models.CharField(
        max_length=2,
        blank=True,
        help_text="2 premières lettres du nom de famille (ex: 'SM' pour Smith)"
    )

    class Meta:
        unique_together = ('cuber', 'group')

    def __str__(self):
        return f"{self.cuber} → {self.group.group_name}"

    @property
    def display_name(self):
        """
        Returns the best available identifier for this student:
          - Both prefixes set → "TOSM"
          - Fallback          → "Rouge Brave Spiderman"
        """
        if self.first_name_prefix and self.last_name_prefix:
            return f"{self.first_name_prefix}{self.last_name_prefix}"
        return str(self.cuber)

    def save(self, *args, **kwargs):
        # Normalize prefixes: uppercase, strip whitespace, hard-cap at 2 chars
        self.first_name_prefix = self.first_name_prefix.strip().upper()[:2]
        self.last_name_prefix = self.last_name_prefix.strip().upper()[:2]
        super().save(*args, **kwargs)