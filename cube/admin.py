from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from .models import CubeState
from .widgets import CubeStateWidget


# ── Blank states for each puzzle size ─────────────────────────────────────

def blank_3x3():
    """All-grey 3×3 state."""
    row = ["X", "X", "X"]
    return {face: [list(row) for _ in range(3)] for face in "ULFRBD"}

def blank_4x4():
    """All-grey 4×4 state."""
    row = ["X", "X", "X", "X"]
    return {face: [list(row) for _ in range(4)] for face in "ULFRBD"}

def blank_5x5():
    """All-grey 5×5 state."""
    row = ["X", "X", "X", "X", "X"]
    return {face: [list(row) for _ in range(5)] for face in "ULFRBD"}


import json

BLANK_STATES = {
    '3': json.dumps({"cube": blank_3x3(), "highlight": {"stickers": []}}),
    '4': json.dumps({"cube": blank_4x4(), "highlight": {"stickers": []}}),
    '5': json.dumps({"cube": blank_5x5(), "highlight": {"stickers": []}}),
}


class CubeStateAdminForm(forms.ModelForm):
    class Meta:
        model = CubeState
        fields = '__all__'
        widgets = {
            "json_state":     CubeStateWidget(),
            "json_highlight": forms.HiddenInput(),
        }

    class Media:
        js = ('cube/js/admin_grid_init.js',)


@admin.register(CubeState)
class CubeStateAdmin(admin.ModelAdmin):
    form = CubeStateAdminForm

    # ── List view ─────────────────────────────────────────────────────────
    list_display  = ("name", "method", "category", "step_number", "difficulty", "hand_orientation")
    list_filter   = ("method", "category", "difficulty", "hand_orientation")
    search_fields = ("name", "slug", "description", "algorithm")
    ordering      = ("method", "category", "step_number")

    # ── Form layout ───────────────────────────────────────────────────────
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Identification', {
            'fields': (
                'name', 'slug', 'method', 'category',
                'step_number', 'difficulty', 'hand_orientation',
            ),
        }),
        ('Cube State', {
            'fields': ('json_state', 'json_highlight'),
            'description': (
                'Set each sticker color. Use X for grey (unknown/hidden). '
                'Select the method above and save first if creating a 4×4 or 5×5 state.'
            ),
        }),
        ('Algorithm', {
            'fields': ('algorithm', 'description'),
        }),
        ('Display Options', {
            'fields': ('setup', 'colored', 'flags'),
            'classes': ('collapse',),
            'description': 'Formerly roofpig_* fields. Used for algorithm animation config.',
        }),
        ('cubing.js Camera', {
            'fields': ('stickering', 'camera_longitude', 'camera_latitude'),
            'classes': ('collapse',),
        }),
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Inject blank state JSON into the page for the JS to use."""
        extra_context = extra_context or {}
        extra_context['blank_states_json'] = mark_safe(json.dumps(BLANK_STATES))
        return super().changeform_view(request, object_id, form_url, extra_context)

    # ── Actions ───────────────────────────────────────────────────────────
    actions = ['duplicate_cube_states']

    def duplicate_cube_states(self, request, queryset):
        """Duplicate selected cube states."""
        count = 0
        for cube_state in queryset:
            cube_state.pk   = None
            cube_state.slug = ''
            cube_state.name = f"{cube_state.name} (Copy)"
            cube_state.save()
            count += 1
        self.message_user(request, f"Successfully duplicated {count} cube state(s).")

    duplicate_cube_states.short_description = "Duplicate selected cube states"