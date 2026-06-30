/**
 * FranContCube — avatar.js
 * ========================
 * Module réutilisable pour :
 *   1. Charger un SVG animal depuis les fichiers statiques Django
 *   2. Rendre les IDs uniques par animal (évite les conflits de gradients)
 *   3. Injecter dynamiquement la couleur du foulard (bandana) avec
 *      calcul automatique de l'ombre et du reflet
 */

// ── Couleurs officielles du Rubik's Cube ──────────────────────────────────────
const CUBE_COLORS = {
    rouge:  '#E8312A',
    orange: '#FF8C00',
    jaune:  '#FFD700',
    vert:   '#00A651',
    bleu:   '#0051A2',
    blanc:  '#E8E8E8',
};

// ── Utilitaires couleur ───────────────────────────────────────────────────────

function hexToRgb(hex) {
    const clean = hex.replace('#', '');
    return {
        r: parseInt(clean.slice(0, 2), 16),
        g: parseInt(clean.slice(2, 4), 16),
        b: parseInt(clean.slice(4, 6), 16),
    };
}

function rgbToHex({ r, g, b }) {
    return '#' + [r, g, b]
        .map(v => Math.max(0, Math.min(255, Math.round(v)))
            .toString(16).padStart(2, '0'))
        .join('');
}

function darken(hex, factor = 0.30) {
    const { r, g, b } = hexToRgb(hex);
    return rgbToHex({ r: r*(1-factor), g: g*(1-factor), b: b*(1-factor) });
}

function lighten(hex, factor = 0.35) {
    const { r, g, b } = hexToRgb(hex);
    return rgbToHex({ r: r+(255-r)*factor, g: g+(255-g)*factor, b: b+(255-b)*factor });
}

function bandanaColors(baseHex) {
    const isWhite = baseHex.toLowerCase() === '#e8e8e8';
    return {
        main:      baseHex,
        shadow:    isWhite ? '#b0b0b0' : darken(baseHex, 0.30),
        highlight: isWhite ? '#ffffff' : lighten(baseHex, 0.40),
    };
}

// ── Cache SVG ─────────────────────────────────────────────────────────────────
const _svgCache = {};

/**
 * Charge un SVG et rend tous ses IDs uniques par animal.
 * Ceci évite les conflits de gradients quand plusieurs SVGs
 * sont présents dans la même page (ex: grille de 12 animaux).
 *
 * Ex: bodyGrad → bodyGrad_hibou, headGrad → headGrad_hibou
 */
async function fetchSVG(animalKey, staticBase) {
    const url = `${staticBase}${animalKey}.svg`;

    if (_svgCache[url]) return _svgCache[url].cloneNode(true);

    const response = await fetch(url);
    if (!response.ok) throw new Error(`SVG introuvable : ${url}`);

    let text = await response.text();

    // ── Rendre les IDs uniques par animal ────────────────────────────────────
    // 1. Trouver tous les IDs définis dans ce SVG
    const idMatches = [...text.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
    const uniqueIds = [...new Set(idMatches)];

    // 2. Remplacer chaque id="X" et chaque url(#X) / href="#X" / xlink:href="#X"
    uniqueIds.forEach(id => {
        const newId = `${id}_${animalKey}`;
        // Remplace id="X" → id="newId"
        text = text.replaceAll(`id="${id}"`, `id="${newId}"`);
        // Remplace url(#X) → url(#newId) dans fill, stroke, etc.
        text = text.replaceAll(`url(#${id})`, `url(#${newId})`);
        // Remplace href="#X" et xlink:href="#X"
        text = text.replaceAll(`href="#${id}"`, `href="#${newId}"`);
        text = text.replaceAll(`xlink:href="#${id}"`, `xlink:href="#${newId}"`);
    });

    const parser = new DOMParser();
    const doc = parser.parseFromString(text, 'image/svg+xml');
    const svgEl = doc.documentElement;

    _svgCache[url] = svgEl.cloneNode(true);
    return svgEl;
}

/**
 * Injecte les couleurs du foulard dans le groupe #bandana_<animal>.
 * - Éléments avec fill (non "none") → couleur principale
 * - Éléments stroke-only (fill="none") → ombre ou reflet selon opacité
 * - linearGradient#scarfGrad_<animal> → mis à jour si présent
 */
function injectBandanaColor(svgEl, animalKey, baseHex) {
    const { main, shadow, highlight } = bandanaColors(baseHex);

    // Le groupe bandana a maintenant l'id "bandana_<animal>"
    const bandana = svgEl.getElementById(`bandana_${animalKey}`);
    if (!bandana) {
        // Fallback : cherche sans suffixe (SVG sans IDs renommés)
        const fallback = svgEl.getElementById('bandana');
        if (!fallback) return;
        _injectIntoGroup(fallback, main, shadow, highlight);
        return;
    }
    _injectIntoGroup(bandana, main, shadow, highlight);

    // Mettre à jour le linearGradient scarfGrad si présent
    const scarfGrad = svgEl.getElementById(`scarfGrad_${animalKey}`);
    if (scarfGrad) {
        const stops = scarfGrad.querySelectorAll('stop');
        if (stops[0]) stops[0].setAttribute('stop-color', lighten(main, 0.10));
        if (stops[1]) stops[1].setAttribute('stop-color', darken(main, 0.20));
    }
}

function _injectIntoGroup(group, main, shadow, highlight) {
    // Éléments avec fill non-"none" → couleur principale du foulard
    group.querySelectorAll('[fill]').forEach(el => {
        const f = el.getAttribute('fill');
        if (f && f !== 'none') {
            el.setAttribute('fill', main);
        }
    });

    // Éléments stroke-only → ombre (opacité > 0.45) ou reflet (≤ 0.45)
    group.querySelectorAll('[fill="none"][stroke]').forEach(el => {
        const opacity = parseFloat(el.getAttribute('opacity') || '1');
        el.setAttribute('stroke', opacity > 0.45 ? shadow : highlight);
    });
}

/**
 * Charge un avatar SVG, injecte la couleur du foulard,
 * et ajuste la taille.
 */
async function loadAvatar(animalKey, colorKey, size = 80, staticBase = '/static/cubing_users/avatars/') {
    const svgEl = await fetchSVG(animalKey, staticBase);

    svgEl.setAttribute('width', size);
    svgEl.setAttribute('height', size);
    svgEl.style.display = 'block';

    const baseHex = CUBE_COLORS[colorKey] || CUBE_COLORS.bleu;
    injectBandanaColor(svgEl, animalKey, baseHex);

    return svgEl;
}

/**
 * Placeholder générique affiché pendant le chargement.
 */
function placeholderAvatar(colorKey, size = 80) {
    const hex = CUBE_COLORS[colorKey] || CUBE_COLORS.bleu;
    const { main } = bandanaColors(hex);
    const div = document.createElement('div');
    div.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 220"
        width="${size}" height="${size}" style="display:block;">
        <ellipse cx="100" cy="215" rx="38" ry="6" fill="#000" opacity="0.07"/>
        <ellipse cx="100" cy="150" rx="50" ry="52" fill="#C8C0B0" stroke="#2C1810" stroke-width="3"/>
        <circle  cx="100" cy="92"  r="50" fill="#C8C0B0" stroke="#2C1810" stroke-width="3"/>
        <path d="M62,138 Q100,150 138,138 Q120,173 100,179 Q80,173 62,138Z"
              fill="${main}" stroke="#2C1810" stroke-width="2"/>
        <circle cx="82"  cy="87" r="13" fill="white" stroke="#2C1810" stroke-width="2"/>
        <circle cx="82"  cy="87" r="8"  fill="#3A1A0A"/>
        <circle cx="82"  cy="87" r="4"  fill="#1A0A0A"/>
        <circle cx="86"  cy="83" r="2.5" fill="white" opacity="0.9"/>
        <circle cx="118" cy="87" r="13" fill="white" stroke="#2C1810" stroke-width="2"/>
        <circle cx="118" cy="87" r="8"  fill="#3A1A0A"/>
        <circle cx="118" cy="87" r="4"  fill="#1A0A0A"/>
        <circle cx="122" cy="83" r="2.5" fill="white" opacity="0.9"/>
        <path d="M90,104 Q100,112 110,104" fill="none" stroke="#2C1810"
              stroke-width="2" stroke-linecap="round"/>
    </svg>`;
    return div.firstChild;
}

// ── Export global ─────────────────────────────────────────────────────────────
window.AvatarLoader = {
    CUBE_COLORS,
    loadAvatar,
    placeholderAvatar,
    bandanaColors,
    darken,
    lighten,

    /**
     * Helper tout-en-un : affiche un placeholder immédiatement,
     * puis remplace par le vrai SVG une fois chargé.
     */
    async render(animalKey, colorKey, size, container, staticBase = '/static/cubing_users/avatars/') {
        if (!animalKey) return;

        // Placeholder immédiat
        container.innerHTML = '';
        container.appendChild(placeholderAvatar(colorKey, size));

        try {
            const svgEl = await loadAvatar(animalKey, colorKey, size, staticBase);
            container.innerHTML = '';
            container.appendChild(svgEl);
        } catch (e) {
            console.warn(`Avatar introuvable pour "${animalKey}" — placeholder conservé.`, e);
        }
    },
};
