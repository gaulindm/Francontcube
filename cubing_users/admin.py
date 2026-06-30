# cubing_users/admin.py
from django.contrib import admin
from .models import Cuber, Leader, Group, GroupMembership, ANIMAL_CHOICES, CUBE_COLOR_CHOICES


@admin.register(Cuber)
class CuberAdmin(admin.ModelAdmin):
    list_display  = ['get_identity', 'animal', 'cube_color', 'get_qualities', 'get_name_prefix', 'created_date', 'last_active_date']
    list_filter   = ['animal', 'cube_color', 'quality_1', 'quality_2', 'created_date']
    search_fields = ['animal', 'cube_color', 'quality_1', 'quality_2', 'first_name_prefix', 'last_name_prefix']
    readonly_fields = ['cuber_id', 'color_code_hash', 'created_date', 'last_active_date']

    def get_identity(self, obj):
        return obj.display_name
    get_identity.short_description = 'Identité'

    def get_qualities(self, obj):
        q1 = dict(obj.QUALITY_CHOICES if hasattr(obj, 'QUALITY_CHOICES') else []).get(obj.quality_1, obj.quality_1)
        q2 = dict(obj.QUALITY_CHOICES if hasattr(obj, 'QUALITY_CHOICES') else []).get(obj.quality_2, obj.quality_2)
        return f"{q1} · {q2}"
    get_qualities.short_description = 'Qualités'

    def get_name_prefix(self, obj):
        if obj.first_name_prefix and obj.last_name_prefix:
            return f"{obj.first_name_prefix}{obj.last_name_prefix}"
        return "—"
    get_name_prefix.short_description = 'Initiales'

    fieldsets = (
        ('Identité visuelle', {
            'fields': ('cuber_id', 'animal', 'cube_color'),
            'description': "L'animal et la couleur du foulard choisis par l'élève à l'inscription."
        }),
        ('Qualités', {
            'fields': ('quality_1', 'quality_2'),
            'description': "Les deux qualités choisies par l'élève, affichées en badges sous l'avatar."
        }),
        ('Identification (leaders seulement)', {
            'fields': ('first_name_prefix', 'last_name_prefix'),
            'description': "2 premières lettres du prénom et du nom (ex: Tommy Smith → TO + SM → TOSM). Jamais affiché à l'élève."
        }),
        ('Sécurité', {
            'fields': ('color_code_hash',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_date', 'last_active_date')
        }),
    )


@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display  = ['get_name', 'role', 'organization', 'created_date']
    list_filter   = ['role', 'created_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'organization']

    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Nom'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display  = ['group_name', 'group_code', 'group_type', 'get_member_count', 'created_date']
    list_filter   = ['group_type', 'created_date']
    search_fields = ['group_name', 'group_code']
    readonly_fields = ['group_id', 'group_code', 'created_date']
    filter_horizontal = ['leaders']

    def get_member_count(self, obj):
        return obj.groupmembership_set.filter(status='active').count()
    get_member_count.short_description = 'Membres actifs'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display  = ['get_cuber', 'get_display_name', 'get_group', 'status', 'joined_date']
    list_filter   = ['status', 'joined_date', 'group', 'cuber__animal', 'cuber__cube_color']
    search_fields = [
        'cuber__animal', 'cuber__quality_1', 'cuber__quality_2',
        'group__group_name',
        'first_name_prefix', 'last_name_prefix',
    ]
    date_hierarchy = 'joined_date'

    def get_cuber(self, obj):
        return obj.cuber.display_name
    get_cuber.short_description = 'Cubeur'

    def get_display_name(self, obj):
        return obj.display_name
    get_display_name.short_description = 'Initiales'

    def get_group(self, obj):
        return obj.group.group_name
    get_group.short_description = 'Groupe'

    fieldsets = (
        ('Appartenance', {
            'fields': ('cuber', 'group', 'status')
        }),
        ('Identification (leaders seulement)', {
            'fields': ('first_name_prefix', 'last_name_prefix'),
            'description': "Visible uniquement du leader. Initialisé depuis le compte cubeur, peut être corrigé par groupe si nécessaire."
        }),
        ('Dates', {
            'fields': ('joined_date',)
        }),
    )
    readonly_fields = ['joined_date']