"""
Step 1a: La Marguerite (The Daisy)

Build the daisy pattern around the yellow center.
This is the first step in solving the Rubik's Cube using the Cubie Newbie method.
"""

from ..base import StepView


class DaisyView(StepView):
    """
    Step 1a: Build the daisy around yellow center.
    
    This is a simple example of using the StepView base class.
    Just define the configuration and you're done!
    """
    
    template_name = "main/methods/cubienewbie/daisy.html"
    step_name = "La Marguerite"
    step_icon = "flower3"
    
    # Map template context variable names to CubeState slugs
    cube_state_slugs = {
        'goal_state': 'marguerite-goal',
        'before_state': 'marguerite-before',
        'after_state': 'marguerite-after',
    }


# Export the view function for URL routing
daisy = DaisyView.as_view()