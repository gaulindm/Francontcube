from cube.models import CubeState
from ..base import StepView, CubeStateLoader


class BottomCrossView(StepView):

    template_name = "main/methods/cubienewbie/bottom-cross.html"
    method_name = "CubieNewbie"
    step_name = "Croix du bas(Jaune)"
    step_number = 1
    step_icon = "plus-circle"

    next_step = "francontcube:beginner_bottom_corners"
    prev_step = None

    cube_state_slugs = {
        'goal_state': 'bottom-cross-goal',
        'before_state': 'bottom-cross-before',
        'after_state': 'bottom-cross-after',
    }


bottom_cross = BottomCrossView.as_view()