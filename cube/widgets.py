from django import forms
import json


class CubeStateWidget(forms.Widget):
    template_name = "cube/widgets/cube_state_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        if value:
            try:
                data = json.loads(value) if isinstance(value, str) else value
            except Exception:
                data = self.default_data()
        else:
            data = self.default_data()

        # 🔒 Guarantee structure
        if not isinstance(data, dict) or "cube" not in data:
            data = self.default_data()

        cube = data.get("cube", self.default_state())
        highlights = data.get("highlight", {}).get("stickers", [])

        # Normalize highlight format into a set for fast lookup
        # Expected format example: ["F-0-1", "U-2-2"]
        highlight_set = set()

        for h in highlights:
            if isinstance(h, str):
                highlight_set.add(h)
            elif isinstance(h, (list, tuple)) and len(h) == 3:
                face, r, c = h
                highlight_set.add(f"{face}-{r}-{c}")
            elif isinstance(h, dict):
                face = h.get("face")
                r = h.get("row")
                c = h.get("col")
                if face is not None:
                    highlight_set.add(f"{face}-{r}-{c}")

        def build_face(face_key):
            face = cube.get(face_key, [["X"] * 3 for _ in range(3)])

            cells = []
            for r in range(3):
                row = []
                for c in range(3):
                    sticker_id = f"{face_key}-{r}-{c}"
                    row.append({
                        "color": face[r][c],
                        "id": sticker_id,
                        "highlight": sticker_id in highlight_set
                    })
                cells.append(row)
            return cells

        # Build all faces for template
        context["faces"] = {
            "U": build_face("U"),
            "L": build_face("L"),
            "F": build_face("F"),
            "R": build_face("R"),
            "B": build_face("B"),
            "D": build_face("D"),
        }

        return context

    def default_data(self):
        return {
            "cube": self.default_state(),
            "highlight": {
                "stickers": []
            }
        }

    def default_state(self):
        return {
            "U": [["X","X","X"], ["X","Y","X"], ["X","X","X"]],
            "D": [["W","W","X"], ["W","W","W"], ["W","W","W"]],
            "F": [["X","X","X"], ["G","G","X"], ["G","G","X"]],
            "B": [["X","X","X"], ["B","B","B"], ["B","B","B"]],
            "R": [["X","X","X"], ["X","O","O"], ["X","O","O"]],
            "L": [["X","X","X"], ["R","R","R"], ["R","R","R"]],
        }