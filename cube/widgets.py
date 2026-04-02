from django import forms
import json


# Colors available in the palette — (value, label)
CUBE_COLORS = [
    ('X', 'Gris / inconnu'),
    ('W', 'Blanc'),
    ('Y', 'Jaune'),
    ('G', 'Vert'),
    ('B', 'Bleu'),
    ('R', 'Rouge'),
    ('O', 'Orange'),
]


class CubeStateWidget(forms.Widget):
    template_name = "cube/widgets/cube_state_widget.html"

    class Media:
        js = (
            'cube/js/cube_state_widget.js',
            'cube/js/admin_grid_init.js',
        )

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # Parse stored JSON
        if value:
            try:
                data = json.loads(value) if isinstance(value, str) else value
            except Exception:
                data = self.default_data()
        else:
            data = self.default_data()

        if not isinstance(data, dict) or "cube" not in data:
            data = self.default_data()

        cube = data.get("cube", self.default_state())

        # Detect grid size from U face
        u_face    = cube.get("U", [])
        grid_size = len(u_face) if u_face else 3

        # Pass the raw JSON value so the template can put it in the textarea
        context['widget'] = type('obj', (object,), {
            'value': value or json.dumps(data),
            'attrs': type('obj', (object,), {
                'name': name,
                'id':   attrs.get('id', f'id_{name}'),
            })(),
        })()

        context['grid_size'] = grid_size
        context['colors']    = CUBE_COLORS

        return context

    def default_data(self):
        return {
            "cube":      self.default_state(),
            "highlight": {"stickers": []},
        }

    def default_state(self):
        """Default solved state — Franco-Ontarian orientation.
        White on top, Yellow on bottom, Green in front,
        Blue in back, Red on right, Orange on left.
        """
        return {
            "U": [["W","W","W"], ["W","W","W"], ["W","W","W"]],
            "D": [["Y","Y","Y"], ["Y","Y","Y"], ["Y","Y","Y"]],
            "F": [["G","G","G"], ["G","G","G"], ["G","G","G"]],
            "B": [["B","B","B"], ["B","B","B"], ["B","B","B"]],
            "R": [["R","R","R"], ["R","R","R"], ["R","R","R"]],
            "L": [["O","O","O"], ["O","O","O"], ["O","O","O"]],
        }

    def value_from_datadict(self, data, files, name):
        """Read the submitted textarea value back on form save."""
        return data.get(name)