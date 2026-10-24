// Filtrowanie i sortowanie bez przeładowywania strony.
(() => {
    "use strict";

    const rowsContainer = document.getElementById('hm-rows');
    const search = document.getElementById('hm-search');
    const sort = document.getElementById('hm-sort');
    const count = document.getElementById('hm-visible-count');
    const tooltip = document.getElementById('hm-tooltip');
    if (!rowsContainer || !search || !sort || !count || !tooltip) return;

    const rows = Array.from(rowsContainer.querySelectorAll('.hm-row'));
    const collator = new Intl.Collator('pl', { sensitivity: 'base', numeric: true });

    function refresh() {
        const searchText = search.value.trim().toLocaleLowerCase('pl');
        const sorted = rows.slice().sort((a, b) => {
            if (sort.value === 'name') {
                return collator.compare(a.dataset.sortName, b.dataset.sortName) || Number(a.dataset.id) - Number(b.dataset.id);
            }
            if (sort.value === 'id') return Number(a.dataset.id) - Number(b.dataset.id);
            return Number(b.dataset.laps) - Number(a.dataset.laps) || Number(a.dataset.id) - Number(b.dataset.id);
        });

        let visible = 0;
        sorted.forEach(row => {
            const matches = (row.dataset.id + ' ' + row.dataset.name).toLocaleLowerCase('pl').includes(searchText);
            row.hidden = !matches;
            // Elementy trafiają na koniec, w kolejności wybranej przez użytkownika.
            rowsContainer.appendChild(row);
            if (matches) visible++;
        });
        count.textContent = `Widocznych: ${visible} z ${rows.length}`;
        tooltip.hidden = true;
    }

    search.addEventListener('input', refresh);
    sort.addEventListener('change', refresh);
    refresh();

    function positionTooltip(event) {
        const gap = 16;
        const left = Math.min(event.clientX + gap, window.innerWidth - tooltip.offsetWidth - 8);
        const top = Math.min(event.clientY + gap, window.innerHeight - tooltip.offsetHeight - 8);
        tooltip.style.left = `${Math.max(8, left)}px`;
        tooltip.style.top = `${Math.max(8, top)}px`;
    }

    rowsContainer.addEventListener('pointermove', event => {
        const segment = event.target.closest('.hm-segment');
        if (!segment) {
            tooltip.hidden = true;
            return;
        }
        const lap = Number(segment.dataset.lap);
        const kind = segment.dataset.kind;
        const description = kind === 'break' ? 'Przerwa'
            : kind === 'open' ? `Okrążenie ${lap} – rozpoczęte, bez zarejestrowanego końca`
            : `Okrążenie ${lap}`;
        tooltip.textContent = `${segment.dataset.name}\n${description}\nOd: ${segment.dataset.start}\nDo: ${segment.dataset.end}${kind === 'open' ? ' (stan na teraz)' : ''}`;
        tooltip.hidden = false;
        positionTooltip(event);
    });
    rowsContainer.addEventListener('pointerleave', () => { tooltip.hidden = true; });
    document.getElementById('hm-search').addEventListener('focus', () => { tooltip.hidden = true; });
})();
