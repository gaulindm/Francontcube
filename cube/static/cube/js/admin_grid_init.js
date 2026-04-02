// cube/static/cube/js/admin_grid_init.js
// Watches the method dropdown and shows a button to reinitialize
// the cube state grid when a 4×4 or 5×5 method is selected.
// Depends on window.reinitWidget exposed by cube_state_widget.js.

(function() {
    'use strict';

    const METHOD_GRID = {
        'reduction-4x4': 4,
        'reduction-5x5': 5,
    };

    document.addEventListener('DOMContentLoaded', function() {
        const methodField = document.getElementById('id_method');
        if (!methodField) return;

        // Create the reinitialize button
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.style.cssText = (
            'margin-left: 12px; padding: 4px 12px; background: #417690; '
            + 'color: white; border: none; border-radius: 4px; cursor: pointer; '
            + 'font-size: 13px; display: none;'
        );
        methodField.parentNode.appendChild(btn);

        function getGridSize(method) {
            return METHOD_GRID[method] || 3;
        }

        function updateButton(method) {
            const size = getGridSize(method);
            if (size !== 3) {
                btn.textContent = `Initialiser grille ${size}×${size}`;
                btn.style.display = 'inline-block';
            } else {
                btn.style.display = 'none';
            }
        }

        btn.addEventListener('click', function() {
            const size   = getGridSize(methodField.value);
            const widget = document.querySelector('[data-widget]');
            if (!widget) return;

            if (typeof window.reinitWidget === 'function') {
                window.reinitWidget(widget, size);
            } else {
                console.error('reinitWidget not found — check cube_state_widget.js is loaded');
            }
        });

        methodField.addEventListener('change', function() {
            updateButton(this.value);
        });

        updateButton(methodField.value);
    });
})();