const jsonFilePath = 'data/latest.json'; // Or dynamically get latest if needed

let currentData = [];
let currentSort = {column: null, direction: 'asc'};

async function loadData() {
    const response = await fetch(jsonFilePath);
    currentData = await response.json();
    renderTable();
}

function renderTable() {
    const tbody = document.querySelector('#dataTable tbody');
    tbody.innerHTML = '';

    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    let filtered = currentData;

    // Apply search term
    if (searchTerm) {
        filtered = filtered.filter(row =>
            Object.values(row).some(value =>
                String(value).toLowerCase().includes(searchTerm)
            )
        );
    }

    // Apply filter dropdown (promotion, old price, both)
    const filterValue = document.getElementById('filter')?.value || 'all';
    filtered = filtered.filter(row => {
        if (filterValue === 'promo') return !!row.promotion;
        if (filterValue === 'old_price') return !!row.old_price;
        if (filterValue === 'both') return !!row.promotion && !!row.old_price;
        return true;
    });

    // Apply sorting
    const sorted = [...filtered];
    if (currentSort.column && currentSort.direction) {
        sorted.sort((a, b) => {
            let valA = a[currentSort.column] || '';
            let valB = b[currentSort.column] || '';

            if (typeof valA === 'string' && typeof valB === 'string') {
                return currentSort.direction === 'asc'
                    ? valA.localeCompare(valB, undefined, {numeric: true, sensitivity: 'base'})
                    : valB.localeCompare(valA, undefined, {numeric: true, sensitivity: 'base'});
            }

            return currentSort.direction === 'asc'
                ? valA - valB
                : valB - valA;
        });
    }

    // Render rows
    sorted.forEach(row => {
        const tr = document.createElement('tr');
        const hasOldPrice = row.old_price && row.old_price !== '';
        const hasPromo = row.promotion && row.promotion !== '';

        if (hasOldPrice && hasPromo) {
            tr.classList.add('has-old-price', 'has-promo');
        } else if (hasOldPrice) {
            tr.classList.add('has-old-price');
        } else if (hasPromo) {
            tr.classList.add('has-promo');
        }

        ['store', 'name', 'price', 'old_price', 'promotion'].forEach(field => {
            const td = document.createElement('td');
            if (field === 'price' || field === 'old_price') {
                td.textContent = formatNumber(row[field]);
            } else {
                td.textContent = row[field] || '';
            }
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

const formatNumber = (value) => {
  const num = parseFloat(value);
  return isNaN(num) ? value : num.toFixed(2);
};

document.addEventListener('DOMContentLoaded', () => {
    loadData();

    // Hook up filters/search/sort if not already
    document.getElementById('searchInput').addEventListener('input', renderTable);
    document.getElementById('filter').addEventListener('change', renderTable);
    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.getAttribute('data-sort');

            // Toggle direction if same column
            if (currentSort.column === column) {
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.column = column;
                currentSort.direction = 'asc';
            }
            renderTable();
        });
    });
});
