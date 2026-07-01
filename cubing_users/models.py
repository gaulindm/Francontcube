# cubing_users/models.py
import uuid
import hashlib
from django.db import models
from django.conf import settings


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES D'IDENTITÉ
# Ces listes définissent les choix valides pour chaque composante de l'avatar.
# L'ordre est important : il détermine l'ordre d'affichage dans l'interface.
# ─────────────────────────────────────────────────────────────────────────────

ANIMAL_CHOICES = [
    ('renard',    'Renard'),
    ('hibou',     'Hibou'),
    ('panda',     'Panda'),
    ('tortue',    'Tortue'),
    ('grenouille','Grenouille'),
    ('lapin',     'Lapin'),
    ('ours',      'Ours'),
    ('castor',    'Castor'),
    ('loup',      'Loup'),
    ('manchot',   'Manchot'),
    ('ecureuil',  'Écureuil'),
    ('perroquet', 'Perroquet'),
]

# Les 6 couleurs officielles du Rubik's Cube.
# La valeur (clé) est le nom CSS/token utilisé dans le SVG du foulard.
CUBE_COLOR_CHOICES = [
    ('rouge',   'Rouge'),
    ('orange',  'Orange'),
    ('jaune',   'Jaune'),
    ('vert',    'Vert'),
    ('bleu',    'Bleu'),
    ('blanc',   'Blanc'),
]

# Valeurs hex correspondantes — utilisées dans les templates et les SVGs.
# Importez ce dict dans vos templates : from cubing_users.models import CUBE_COLOR_HEX
CUBE_COLOR_HEX = {
    'rouge':  '#E8312A',
    'orange': '#FF8C00',
    'jaune':  '#FFD700',
    'vert':   '#00A651',
    'bleu':   '#0051A2',
    'blanc':  '#F0F0F0',
}

QUALITY_CHOICES = [
    ('curieux',      'Curieux·se'),
    ('intelligent',  'Intelligent·e'),
    ('rapide',       'Rapide'),
    ('determine',    'Déterminé·e'),
    ('perseverant',  'Persévérant·e'),
    ('concentre',    'Concentré·e'),
    ('gentil',       'Gentil·le'),
    ('aidant',       'Aidant·e'),
    ('creatif',      'Créatif·ve'),
    ('joyeux',       'Joyeux·se'),
    ('patient',      'Patient·e'),
    ('courageux',    'Courageux·se'),
    ('prudent',      'Prudent·e'),
    ('confiant',     'Confiant·e'),
    ('calme',        'Calme'),
]

# Icônes associées aux qualités (Bootstrap Icons).
# Utilisez ce dict dans vos templates pour afficher les badges.
QUALITY_ICONS = {
    'curieux':     'bi-search',
    'intelligent': 'bi-lightbulb',
    'rapide':      'bi-lightning',
    'determine':   'bi-trophy',
    'perseverant': 'bi-arrow-repeat',
    'concentre':   'bi-bullseye',
    'gentil':      'bi-heart',
    'aidant':      'bi-hand-thumbs-up',
    'creatif':     'bi-palette',
    'joyeux':      'bi-emoji-smile',
    'patient':     'bi-hourglass-split',
    'courageux':   'bi-shield',
    'prudent':     'bi-puzzle',
    'confiant':    'bi-star',
    'calme':       'bi-water',
}


# ─────────────────────────────────────────────────────────────────────────────
# MODÈLES
# ─────────────────────────────────────────────────────────────────────────────

class Cuber(models.Model):
    """
    Utilisateur cubeur anonyme (typiquement un enfant).

    Identité visuelle
    -----------------
    Chaque cubeur possède un avatar composé de trois éléments choisis
    à l'inscription :
      • animal    — un des 12 animaux de la collection FranContCube
      • cube_color — une des 6 couleurs officielles du Rubik's Cube
                    (détermine la couleur du foulard sur l'avatar SVG)
      • quality_1 / quality_2 — deux qualités personnelles parmi 15,
                    affichées en badges sous l'avatar

    Le SVG de l'avatar est rendu dynamiquement via le template tag
    `{% avatar_svg cuber %}` (voir cubing_users/templatetags/avatar_tags.py).
    Le foulard hérite automatiquement de `cube_color`.

    Animation future
    ----------------
    Les couches SVG sont nommées et groupées (#body, #eyes, #bandana,
    #shadow) afin de permettre des animations CSS/JS ultérieures sans
    modifier la structure du fichier SVG.

    Identification pour les leaders
    ---------------------------------
    Les préfixes de nom (first_name_prefix / last_name_prefix) sont
    visibles uniquement des leaders pour faciliter la gestion des comptes.
    Ils ne sont jamais montrés à l'élève.
    """

    cuber_id        = models.UUIDField(primary_key=True, default=uuid.uuid4)
    color_code_hash = models.CharField(max_length=128)
    created_date    = models.DateTimeField(auto_now_add=True)
    last_active_date= models.DateTimeField(auto_now=True)

    # ── Identité de l'avatar ───────────────────────────────────────────────
    animal = models.CharField(
        max_length=20,
        choices=ANIMAL_CHOICES,
        default='hibou',
        help_text="Animal choisi par l'élève à l'inscription (1 parmi 12)"
    )
    cube_color = models.CharField(
        max_length=10,
        choices=CUBE_COLOR_CHOICES,
        default='bleu',
        help_text="Couleur du foulard — les 6 couleurs officielles du Rubik's Cube"
    )
    quality_1 = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        default='curieux',
        help_text="Première qualité choisie par l'élève (affichée en badge)"
    )
    quality_2 = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        default='perseverant',
        help_text="Deuxième qualité choisie par l'élève (affichée en badge)"
    )

    # ── Lien optionnel vers compte traditionnel ────────────────────────────
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
        help_text="2 premières lettres du prénom (ex: 'TO' pour Tommy) — leaders seulement"
    )
    last_name_prefix = models.CharField(
        max_length=2,
        blank=True,
        help_text="2 premières lettres du nom de famille (ex: 'SM' pour Smith) — leaders seulement"
    )

    class Meta:
        verbose_name = 'Cubeur'
        verbose_name_plural = 'Cubeurs'

    # ── Représentations ────────────────────────────────────────────────────

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        """
        Nom affiché à l'élève, ex: « Hibou Courageux ».
        Toujours basé sur l'animal et la première qualité.
        """
        animal_label   = dict(ANIMAL_CHOICES).get(self.animal, self.animal).capitalize()
        quality_label  = dict(QUALITY_CHOICES).get(self.quality_1, self.quality_1).capitalize()
        return f"{animal_label} {quality_label}"

    @property
    def bandana_hex(self):
        """Retourne le code hex du foulard, prêt à injecter dans le SVG."""
        return CUBE_COLOR_HEX.get(self.cube_color, '#0051A2')

    @property
    def quality_1_icon(self):
        return QUALITY_ICONS.get(self.quality_1, 'bi-star')

    @property
    def quality_2_icon(self):
        return QUALITY_ICONS.get(self.quality_2, 'bi-star')

    @property
    def avatar_svg_path(self):
        """
        Chemin vers le fichier SVG de base de l'animal.
        Convention : static/cubing_users/avatars/<animal>.svg
        La couleur du foulard est injectée dynamiquement via le template tag.
        """
        return f"cubing_users/avatars/{self.animal}.svg"

    # ── Méthodes ──────────────────────────────────────────────────────────

    def save(self, *args, **kwargs):
        # Normalize prefixes: uppercase, strip whitespace, hard-cap at 2 chars
        self.first_name_prefix = self.first_name_prefix.strip().upper()[:2]
        self.last_name_prefix  = self.last_name_prefix.strip().upper()[:2]
        super().save(*args, **kwargs)

    def set_color_code(self, plain_color_code: str):
        """
        Hash et stocke un nouveau code couleur (SHA256).
        Appeler save() après pour persister.

        Le code est normalisé en string avant le hash :
          - liste  → 'Rouge,Bleu,Vert'
          - string → utilisé tel quel

        Usage:
            cuber.set_color_code("Rouge,Bleu,Rouge")
            cuber.save()
        """
        if isinstance(plain_color_code, list):
            plain_color_code = ','.join(plain_color_code)
        self.color_code_hash = hashlib.sha256(plain_color_code.encode()).hexdigest()

    def qualities_display(self):
        """
        Retourne la liste des deux qualités sous forme de dicts prêts
        pour le template : [{'label': '...', 'icon': '...'}, ...]
        """
        quality_map = dict(QUALITY_CHOICES)
        return [
            {'key': self.quality_1, 'label': quality_map.get(self.quality_1, ''), 'icon': self.quality_1_icon},
            {'key': self.quality_2, 'label': quality_map.get(self.quality_2, ''), 'icon': self.quality_2_icon},
        ]


class LeaderRequest(models.Model):
    """
    Demande d'accès Leader soumise via le formulaire public.
    En attente d'approbation manuelle par l'administrateur.
    Une fois approuvée, un compte User + Leader est créé automatiquement.
    """

    ROLE_CHOICES = [
        ('teacher',      'Enseignant'),
        ('coach',        'Entraîneur'),
        ('club_leader',  'Animateur de Club'),
        ('parent',       'Parent Responsable'),
    ]

    first_name    = models.CharField(max_length=150, verbose_name='Prénom')
    last_name     = models.CharField(max_length=150, verbose_name='Nom de famille')
    email         = models.EmailField(unique=True, verbose_name='Adresse courriel')
    role          = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='Rôle')
    organization  = models.CharField(max_length=200, blank=True, verbose_name='Organisation')
    # Mot de passe haché — stocké temporairement jusqu'à l'approbation
    password_hash = models.CharField(max_length=256)
    submitted_date = models.DateTimeField(auto_now_add=True, verbose_name='Date de demande')
    is_approved   = models.BooleanField(default=False, verbose_name='Approuvée')
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="Date d'approbation")

    class Meta:
        verbose_name = 'Demande Leader'
        verbose_name_plural = 'Demandes Leader'
        ordering = ['-submitted_date']

    def __str__(self):
        status = '✅' if self.is_approved else '⏳'
        return f"{status} {self.first_name} {self.last_name} ({self.email})"


class Leader(models.Model):
    """Leader (prof/coach) — utilise l'auth traditionnelle Django."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leader_profile'
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('teacher',      'Enseignant'),
            ('coach',        'Entraîneur'),
            ('club_leader',  'Animateur de Club'),
            ('parent',       'Parent Responsable'),
        ]
    )
    organization  = models.CharField(max_length=200, blank=True)
    created_date  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Leader'
        verbose_name_plural = 'Leaders'

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.get_role_display()}"


class Group(models.Model):
    """Classe ou club de cubing."""

    group_id   = models.UUIDField(primary_key=True, default=uuid.uuid4)
    group_name = models.CharField(max_length=200)
    group_code = models.CharField(max_length=6, unique=True)
    group_type = models.CharField(
        max_length=20,
        choices=[
            ('class',    'Classe'),
            ('club',     'Club'),
            ('team',     'Équipe'),
            ('practice', 'Groupe de Pratique'),
        ]
    )
    leaders      = models.ManyToManyField(Leader, related_name='groups')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Groupe'
        verbose_name_plural = 'Groupes'

    def __str__(self):
        return self.group_name


class GroupMembership(models.Model):
    """Relation N-to-N Cuber ↔ Group."""

    cuber       = models.ForeignKey(Cuber, on_delete=models.CASCADE)
    group       = models.ForeignKey(Group, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)
    status      = models.CharField(
        max_length=20,
        choices=[
            ('active',   'Actif'),
            ('inactive', 'Inactif'),
        ],
        default='active'
    )

    # ── Identification visible des leaders uniquement ──────────────────────
    # Initialisé depuis Cuber.first_name_prefix / last_name_prefix lors de
    # l'adhésion au groupe. Le leader peut corriger par groupe si nécessaire.
    # Affiché sous forme "TOSM" (Tommy Smith) — jamais montré à l'élève.
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
        verbose_name = 'Adhésion au groupe'
        verbose_name_plural = 'Adhésions aux groupes'

    def __str__(self):
        return f"{self.cuber} → {self.group.group_name}"

    @property
    def display_name(self):
        """
        Identifiant affiché au leader dans la liste de classe :
          - Les deux préfixes sont définis → "TOSM"
          - Sinon → nom d'affichage de l'avatar, ex: "Hibou Courageux"
        """
        if self.first_name_prefix and self.last_name_prefix:
            return f"{self.first_name_prefix}{self.last_name_prefix}"
        return str(self.cuber)

    def save(self, *args, **kwargs):
        self.first_name_prefix = self.first_name_prefix.strip().upper()[:2]
        self.last_name_prefix  = self.last_name_prefix.strip().upper()[:2]
        super().save(*args, **kwargs)
