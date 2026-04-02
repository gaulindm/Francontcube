// cube/static/cube/js/cube_state_widget.js
// Interactive cube state editor for the Django admin widget.
// Works for 3×3, 4×4, and 5×5 — grid size is read from data-grid-size.
//
// Click       → paint the cell with the selected colour
// Shift+click → toggle the highlight glow on a cell
//
// Stickers are stored as arrays [face, row, col] to match cube_renderer.js.

const COLOR_MAP = {
    W: "#fff",
    Y: "#ff0",
    G: "#0a0",
    B: "#00c",
    R: "#e00",
    O: "#f80",
    X: "#ccc",
};

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-widget]").forEach(initCubeWidget);
});

/**
 * Initialize one cube widget.
 * @param {HTMLElement} widget — the [data-widget] container
 */
function initCubeWidget(widget) {
    const textarea = widget.querySelector("textarea");
    if (!textarea) return;

    // Parse stored JSON — shaped as {cube, highlight: {stickers: []}}
    let data;
    try {
        const parsed = JSON.parse(textarea.value);
        data = (parsed && typeof parsed === "object") ? parsed : {};
    } catch (_) {
        data = {};
    }

    if (!data.cube)                              data.cube      = {};
    if (!data.highlight)                         data.highlight = { stickers: [] };
    if (!Array.isArray(data.highlight.stickers)) data.highlight.stickers = [];

    // Normalise any legacy {face, row, col} objects to [face, row, col] arrays.
    // This cleans up records saved by older widget versions so they display
    // correctly and are written back in the canonical format on next save.
    data.highlight.stickers = data.highlight.stickers.map(s =>
        Array.isArray(s) ? s : [s.face, s.row, s.col]
    );

    const gridSize = parseInt(widget.dataset.gridSize || "3", 10);
    const stickers = data.highlight.stickers; // shared mutable reference

    // ── Palette ───────────────────────────────────────────────────────────
    let selectedColor = "W";

    widget.querySelectorAll(".cube-color").forEach(btn => {
        btn.addEventListener("click", () => {
            widget.querySelectorAll(".cube-color")
                  .forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            selectedColor = btn.dataset.color;
        });
    });

    // ── Build face grids ──────────────────────────────────────────────────
    widget.querySelectorAll(".cube-face").forEach(faceEl => {
        buildFace(faceEl, data, gridSize, textarea, stickers, () => selectedColor);
    });
}

/**
 * Return true if [face, r, c] exists in the stickers array.
 * Stickers are stored as [face, row, col] arrays.
 */
function stickerIndex(stickers, face, r, c) {
    return stickers.findIndex(
        s => Array.isArray(s) && s[0] === face && s[1] === r && s[2] === c
    );
}

/**
 * Build the cell grid for one face.
 */
function buildFace(faceEl, data, gridSize, textarea, stickers, getColor) {
    const face = faceEl.dataset.face;
    const grid = faceEl.querySelector(".cube-grid");
    if (!grid) return;

    grid.innerHTML = "";

    if (!data.cube[face]) {
        data.cube[face] = Array.from(
            { length: gridSize },
            () => Array(gridSize).fill("X")
        );
    }

    for (let r = 0; r < gridSize; r++) {
        for (let c = 0; c < gridSize; c++) {
            const color = (data.cube[face][r] && data.cube[face][r][c]) || "X";

            const cell = document.createElement("div");
            cell.className        = "cube-cell";
            cell.style.background = COLOR_MAP[color] || COLOR_MAP.X;

            // Restore highlight on load
            if (stickerIndex(stickers, face, r, c) !== -1) {
                cell.classList.add("highlight");
            }

            cell.addEventListener("click", (e) => {
                if (e.shiftKey) {
                    // ── Shift+click: toggle highlight ─────────────────────
                    const idx = stickerIndex(stickers, face, r, c);
                    if (idx === -1) {
                        stickers.push([face, r, c]);   // ← array format
                        cell.classList.add("highlight");
                    } else {
                        stickers.splice(idx, 1);
                        cell.classList.remove("highlight");
                    }
                    saveState(textarea, data);

                } else {
                    // ── Regular click: paint colour ───────────────────────
                    const chosen = getColor();
                    if (!data.cube[face][r]) {
                        data.cube[face][r] = Array(gridSize).fill("X");
                    }
                    data.cube[face][r][c] = chosen;
                    cell.style.background = COLOR_MAP[chosen] || COLOR_MAP.X;
                    saveState(textarea, data);
                }
            });

            grid.appendChild(cell);
        }
    }
}

/**
 * Write the full {cube, highlight} blob back to the json_state textarea.
 * Everything lives here — do not touch any other field.
 */
function saveState(textarea, data) {
    textarea.value = JSON.stringify(data);
}

/**
 * Re-initialize a widget with a new blank state.
 * Called by admin_grid_init.js when the method changes.
 */
function reinitWidget(widget, gridSize) {
    const textarea = widget.querySelector("textarea");
    if (!textarea) return;

    const row  = Array(gridSize).fill("X");
    const cube = {};
    ["U", "L", "F", "R", "B", "D"].forEach(face => {
        cube[face] = Array.from({ length: gridSize }, () => [...row]);
    });

    const data = { cube, highlight: { stickers: [] } };
    textarea.value = JSON.stringify(data);

    widget.dataset.gridSize = String(gridSize);

    let selectedColor = "W";

    widget.querySelectorAll(".cube-face").forEach(faceEl => {
        buildFace(
            faceEl, data, gridSize, textarea,
            data.highlight.stickers, () => selectedColor
        );
    });

    // Clone palette buttons to remove stale listeners
    widget.querySelectorAll(".cube-color").forEach(btn => {
        const fresh = btn.cloneNode(true);
        btn.parentNode.replaceChild(fresh, btn);
        fresh.classList.remove("active");
        fresh.addEventListener("click", () => {
            widget.querySelectorAll(".cube-color")
                  .forEach(b => b.classList.remove("active"));
            fresh.classList.add("active");
            selectedColor = fresh.dataset.color;
        });
    });

    const first = widget.querySelector(".cube-color");
    if (first) first.classList.add("active");
}

window.reinitWidget = reinitWidget;