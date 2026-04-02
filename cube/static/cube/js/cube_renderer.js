export function renderCube(svgElement, cubeState) {

    const COLOR_MAP = {
        W: "#ffffff",
        Y: "#ffff00",
        R: "#ff0000",
        O: "#ff8000",
        B: "#0000ff",
        G: "#00cc00",
        X: "#CCCCCC",
    };

    const faces = ["U", "R", "F", "D", "L", "B"];

    // 🔑 Support BOTH old and new data shapes
    const cube = cubeState.cube ? cubeState.cube : cubeState;
    const highlights = cubeState.highlight?.stickers || [];

    function isHighlighted(face, r, c) {
        return highlights.some(s => {
            if (Array.isArray(s)) {
                return s[0] === face && s[1] === r && s[2] === c;
            }
            // Legacy format saved as {face, row, col} objects
            return s.face === face && s.row === r && s.col === c;
        });
    }

    function getSticker(face, r, c) {
        const id = `sticker-${face}-${r}-${c}`;
        return svgElement.getElementById(id) || document.getElementById(id);
    }

    // ── Pass 1: fill colours and reset all strokes to default ────────────
    faces.forEach(face => {
        const grid = cube[face];
        if (!grid) return;

        for (let r = 0; r < grid.length; r++) {
            for (let c = 0; c < grid.length; c++) {
                const sticker = getSticker(face, r, c);
                if (!sticker) continue;

                sticker.setAttribute("fill", COLOR_MAP[grid[r][c]] || grid[r][c]);
                sticker.setAttribute("stroke", "#000");
                sticker.setAttribute("stroke-width", "1");
                sticker.style.filter = "";
            }
        }
    });

    // ── Pass 2: apply highlight last so it is never covered by neighbours ─
    faces.forEach(face => {
        const grid = cube[face];
        if (!grid) return;

        for (let r = 0; r < grid.length; r++) {
            for (let c = 0; c < grid.length; c++) {
                if (!isHighlighted(face, r, c)) continue;

                const sticker = getSticker(face, r, c);
                if (!sticker) continue;

                sticker.setAttribute("stroke", "#ffcc00");
                sticker.setAttribute("stroke-width", "5");
                sticker.style.filter = "drop-shadow(0 0 10px #ffcc00) drop-shadow(0 0 4px #ff8800)";

                // Move to end of parent so it renders above all siblings
                sticker.parentNode?.appendChild(sticker);
            }
        }
    });
}