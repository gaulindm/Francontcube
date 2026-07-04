# badges/admin.py
from django.contrib import admin
from .models import Badge, CuberBadge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'family', 'has_custom_icon', 'is_brevet', 'active', 'display_order')
    list_filter = ('family', 'is_brevet', 'active')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('requires_badges',)


@admin.register(CuberBadge)
class CuberBadgeAdmin(admin.ModelAdmin):
    list_display = (
        'cuber', 'badge', 'status_display',
        'auto_track_complete', 'quiz_complete',
        'requested_date', 'validated_date',
    )
    list_filter = ('badge__family', 'badge', 'validated_date')
    search_fields = ('cuber__animal', 'cuber__cube_color')
    actions = ['approuver']

    def status_display(self, obj):
        return obj.status
    status_display.short_description = 'Statut'

    @admin.action(description="Approuver les écussons sélectionnés")
    def approuver(self, request, queryset):
        # Même logique que l'approbation de LeaderRequest: le compte admin
        # qui clique doit être lié à un profil Leader.
        leader = getattr(request.user, 'leader_profile', None)
        if leader is None:
            self.message_user(
                request,
                "Ton compte admin n'est pas lié à un profil Leader — "
                "impossible d'approuver.",
                level='error',
            )
            return

        count = 0
        for cuberbadge in queryset:
            if cuberbadge.status == 'en_attente':
                cuberbadge.validate(leader)
                count += 1

        self.message_user(request, f"{count} écusson(s) approuvé(s).")