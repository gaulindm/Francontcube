"""
main/views/puzzles/puzzle_base.py

Shared helpers and generic view functions used by puzzle_4x4.py and puzzle_5x5.py.
Neither of those files needs to repeat this code — they just import what they need.
"""

from django.shortcuts import render
from django.http import Http404
from cube.models import CubeState
import json


# ── Helpers ───────────────────────────────────────────────────────────────

def get_cube_state(slug):
    """Fetch a CubeState json_state by slug. Returns JSON string or None."""
    try:
        state = CubeState.objects.get(slug=slug)
        return json.dumps(state.json_state)
    except CubeState.DoesNotExist:
        return None


def get_step_info(config, step_slug):
    """
    Look up a step by slug within a config dict.
    Returns (step_info, prev_step, next_step) or raises Http404.
    """
    steps     = config['steps']
    step_info = next((s for s in steps if s['slug'] == step_slug), None)
    if not step_info:
        raise Http404(f"Étape inconnue : {step_slug}")
    idx       = [s['slug'] for s in steps].index(step_slug)
    prev_step = steps[idx - 1] if idx > 0 else None
    next_step = steps[idx + 1] if idx < len(steps) - 1 else None
    return step_info, prev_step, next_step


# ── Generic views ─────────────────────────────────────────────────────────
# Each specific puzzle file calls these with its own config, reference pages,
# and named_states function.  The template path is derived from puzzle_type
# so 4×4 and 5×5 each resolve to their own folder automatically.

def puzzle_home(request, config):
    """Landing page — lists all steps for this puzzle."""
    puzzle_type = config['puzzle_type']
    return render(
        request,
        f'main/puzzles/{puzzle_type}/home.html',
        {
            'puzzle_type': puzzle_type,
            'name':        config['name'],
            'steps':       config['steps'],
            'home_url':    config['home_url'],
            'step_url':    config['step_url'],
            'ref_url':     config.get('ref_url'),
        },
    )


def puzzle_step(request, config, step_slug, named_states_fn):
    """
    One sequential step page.
    named_states_fn(slug) must return a dict of context variables for that step.
    """
    puzzle_type                     = config['puzzle_type']
    step_info, prev_step, next_step = get_step_info(config, step_slug)

    context = {
        'puzzle_type': puzzle_type,
        'name':        config['name'],
        'step':        step_info,
        'prev_step':   prev_step,
        'next_step':   next_step,
        'home_url':    config['home_url'],
        'step_url':    config['step_url'],
        'ref_url':     config.get('ref_url'),
    }
    context.update(named_states_fn(step_slug))

    return render(request, f'main/puzzles/{puzzle_type}/{step_slug}.html', context)


def puzzle_reference(request, config, reference_pages, ref_slug, named_states_fn):
    """
    Standalone reference page (e.g. parity).
    Not a sequential step — no prev/next navigation.
    """
    puzzle_type = config['puzzle_type']
    ref_info    = reference_pages.get(ref_slug)
    if not ref_info:
        raise Http404(f"Page de référence inconnue : {ref_slug}")

    context = {
        'puzzle_type': puzzle_type,
        'name':        config['name'],
        'ref':         ref_info,
        'home_url':    config['home_url'],
        'step_url':    config['step_url'],
        'ref_url':     config.get('ref_url'),
    }
    context.update(named_states_fn(ref_slug))

    return render(request, f'main/puzzles/{puzzle_type}/{ref_slug}.html', context)