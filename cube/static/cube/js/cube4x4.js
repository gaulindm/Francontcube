// cube4x4.js — colours a 4x4 isometric SVG from a 96-char facelet string
// Facelet order: U(0-15) R(16-31) F(32-47) D(48-63) L(64-79) B(80-95)

const PALETTE = {
  U: '#FFFFFF', R: '#D32F2F', F: '#2E7D32',
  D: '#FFEB3B', L: '#F57C00', B: '#1565C0',
};

const FACES = [
  ['U', 0], ['R', 16], ['F', 32],
  ['D', 48], ['L', 64], ['B', 80],
];

function buildIdMap() {
  const map = {};
  for (const [face, start] of FACES) {
    for (let i = 0; i < 16; i++) {
      map[start + i] = `sticker-${face}-${Math.floor(i / 4)}-${i % 4}`;
    }
  }
  return map;
}

const ID_MAP = buildIdMap();

export function applyState(svgEl, stateStr) {
  if (!stateStr || stateStr.length !== 96) return;
  for (let i = 0; i < 96; i++) {
    const el = svgEl.getElementById(ID_MAP[i]);
    if (el) el.setAttribute('fill', PALETTE[stateStr[i]] ?? '#CCC');
  }
}

export function initAllCubes() {
  document.querySelectorAll('svg[data-puzzle="4x4"]').forEach(svg => {
    const state = svg.dataset.state;
    if (state) applyState(svg, state);

    // Click to cycle colors (dev/admin helper — remove in prod if you want)
    svg.querySelectorAll('.sticker').forEach(el => {
      el.addEventListener('click', () => {
        const colors = Object.values(PALETTE);
        const cur = el.getAttribute('fill');
        const next = colors[(colors.indexOf(cur) + 1) % colors.length];
        el.setAttribute('fill', next ?? colors[0]);
      });
    });
  });
}

// Auto-init when loaded as a plain <script> (non-module pages)
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', initAllCubes);
}