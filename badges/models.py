# badges/models.py
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from cubing_users.models import Cuber, Leader


class Badge(models.Model):
    """
    Définition statique d'un écusson (le catalogue, comme les brevets scouts).
    Une ligne ici = un type d'écusson que n'importe quel cubeur peut viser.
    """

    FAMILY_CHOICES = [
        ('cubie-newbie', 'Cubie-Newbie'),
        ('curieux', 'Cubie-Curieux'),
        ('f2l', 'F2L'),
        ('oll', 'OLL'),
        ('pll', 'PLL'),
        ('avance', 'Avancé'),
        ('meta', 'Méta'),
        ('brevet', 'Brevet (regroupement)'),
    ]

    badge_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=60)
    name = models.CharField(max_length=100)
    icon = models.CharField(
        max_length=10, blank=True,
        help_text="Emoji de secours, affiché tant que le SVG n'existe pas. Ex: 🏆"
    )
    has_custom_icon = models.BooleanField(
        default=False,
        help_text=(
            "Coche une fois que badges/static/badges/icons/{slug}.png existe. "
            "Icônes composées dans Inkscape à partir d'un rendu CubeState + "
            "d'une forme d'écusson."
        )
    )
    family = models.CharField(max_length=20, choices=FAMILY_CHOICES)

    description = models.TextField(
        blank=True,
        help_text="Ce que le cubeur voit: à quoi sert cet écusson"
    )
    criteria_description = models.TextField(
        blank=True,
        help_text="Ce que le leader voit lors de la validation: comment vérifier"
    )

    # Modes de déblocage — chaque mode coché doit être rempli avant que
    # l'écusson passe en attente de validation.
    requires_auto_track = models.BooleanField(
        default=False,
        help_text="Débloqué en partie par le minuteur / la pratique enregistrée"
    )
    requires_quiz = models.BooleanField(
        default=False,
        help_text="Débloqué en partie par un mini-quiz réussi"
    )
    requires_leader_validation = models.BooleanField(
        default=True,
        help_text="Un leader doit approuver avant que l'écusson soit officiellement débloqué"
    )

    # Critères flexibles — évite une migration à chaque ajustement de seuil.
    # Exemples:
    #   {"category": "corner-in-slot", "min_cases": 8}
    #   {"threshold_seconds": 120}
    #   {"streak_days": 5, "window_days": 7}
    criteria = models.JSONField(default=dict, blank=True)

    # Brevets: badge qui se débloque automatiquement quand ses prérequis le sont.
    is_brevet = models.BooleanField(default=False)
    requires_badges = models.ManyToManyField(
        'self', symmetrical=False, blank=True,
        related_name='required_for',
        help_text="Pour les brevets: écussons qui doivent tous être débloqués"
    )

    display_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(
        default=True,
        help_text="Décoche pour cacher temporairement un écusson en construction"
    )

    class Meta:
        ordering = ['family', 'display_order', 'name']

    def __str__(self):
        return f"{self.icon} {self.name}".strip()

    @property
    def icon_static_path(self):
        """Chemin statique attendu si has_custom_icon est coché."""
        return f"badges/icons/{self.slug}.png" if self.has_custom_icon else None

    def clean(self):
        if self.is_brevet and (self.requires_auto_track or self.requires_quiz):
            raise ValidationError(
                "Un brevet se débloque par agrégation de ses prérequis, "
                "pas par auto-track ou quiz."
            )


class CuberBadge(models.Model):
    """
    Progrès d'un cubeur spécifique vers un écusson spécifique.
    Une ligne n'existe que si le cubeur a entamé sa progression —
    pas de pré-création pour tous les cubeurs x tous les badges.
    """

    cuberbadge_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cuber = models.ForeignKey(Cuber, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='cuber_progress')

    auto_track_complete = models.BooleanField(default=False)
    quiz_complete = models.BooleanField(default=False)

    requested_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Date à laquelle auto-track + quiz ont été complétés (entrée en file d'attente)"
    )

    validated_by = models.ForeignKey(
        Leader, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='badges_validated'
    )
    validated_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('cuber', 'badge')
        ordering = ['-requested_date']

    def __str__(self):
        return f"{self.cuber.display_name} — {self.badge.name} ({self.status})"

    @property
    def status(self):
        """
        Statut dérivé — jamais stocké directement, pour éviter toute
        désynchronisation avec les champs sources.
        Valeurs possibles: 'en_cours', 'en_attente', 'debloque'
        """
        if self.validated_date:
            return 'debloque'

        criteria_met = True
        if self.badge.requires_auto_track and not self.auto_track_complete:
            criteria_met = False
        if self.badge.requires_quiz and not self.quiz_complete:
            criteria_met = False

        if criteria_met:
            return 'debloque' if not self.badge.requires_leader_validation else 'en_attente'

        return 'en_cours'

    def check_and_mark_pending(self):
        """
        À appeler après toute mise à jour de auto_track_complete ou
        quiz_complete. Fixe requested_date la première fois que les
        critères sont remplis (utile pour trier la file d'attente du leader).
        """
        if self.status == 'en_attente' and not self.requested_date:
            self.requested_date = timezone.now()
            self.save(update_fields=['requested_date'])

    def validate(self, leader):
        """Le leader approuve l'écusson — appelé depuis l'action admin."""
        self.validated_by = leader
        self.validated_date = timezone.now()
        self.save(update_fields=['validated_by', 'validated_date'])
        self._maybe_unlock_brevets()

    def complete_self_check(self):
        """
        Marque la partie quiz/confirmation comme complétée par le cubeur
        lui-même (honor system). Si le badge ne requiert ni auto-track
        supplémentaire ni validation leader, il se débloque immédiatement.

        validated_date est posé même sans leader (nécessaire pour que
        l'agrégation des brevets fonctionne) — validated_by reste vide
        pour qu'on puisse toujours distinguer une auto-validation d'une
        validation par un adulte.
        """
        self.quiz_complete = True
        update_fields = ['quiz_complete']

        if self.status == 'debloque' and not self.validated_date:
            self.validated_date = timezone.now()
            update_fields.append('validated_date')

        self.save(update_fields=update_fields)

        if self.validated_date:
            self._maybe_unlock_brevets()

    def _maybe_unlock_brevets(self):
        """
        Après un déblocage, vérifie si ça complète un brevet
        (ex: les 8 écussons F2L complètent 'Maître F2L').
        """
        candidate_brevets = Badge.objects.filter(
            is_brevet=True, requires_badges=self.badge, active=True
        )
        for brevet in candidate_brevets:
            required_ids = set(brevet.requires_badges.values_list('pk', flat=True))
            if not required_ids:
                continue

            unlocked_ids = set(
                CuberBadge.objects.filter(
                    cuber=self.cuber,
                    badge_id__in=required_ids,
                    validated_date__isnull=False
                ).values_list('badge_id', flat=True)
            )

            if required_ids <= unlocked_ids:
                CuberBadge.objects.get_or_create(
                    cuber=self.cuber, badge=brevet,
                    defaults={'validated_date': timezone.now()}
                )