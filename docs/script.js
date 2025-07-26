const jsonFilePath = 'data/latest.json'; // Or dynamically get latest if needed

async function loadData() {
  const response = await fetch(jsonFilePath);
  currentData = await response.json();

  const selectedFilter = document.getElementById('filter')?.value || 'all';
  renderTable(currentData, selectedFilter);
}

function renderTable(data, filter = 'all') {
  const tbody = document.querySelector('#dataTable tbody');
  tbody.innerHTML = '';

  // Apply filter
  const filtered = data.filter(row => {
    const hasOldPrice = row.old_price && row.old_price !== '';
    const hasPromo = row.promotion && row.promotion !== '';

    return !((filter === 'old_price' && !hasOldPrice) ||
        (filter === 'promotion' && !hasPromo) ||
        (filter === 'both' && !(hasOldPrice && hasPromo)));
  });

  // Sort based on currentSort
  const sorted = [...filtered];
  if (currentSort.column && currentSort.direction) {
    data.sort((a, b) => {
      let valA = a[currentSort.column] || '';
      let valB = b[currentSort.column] || '';

      // Case-insensitive comparison if values are strings
      if (typeof valA === 'string' && typeof valB === 'string') {
        valA = valA.toLowerCase();
        valB = valB.toLowerCase();
      }

      if (valA < valB) return currentSort.direction === 'asc' ? -1 : 1;
      if (valA > valB) return currentSort.direction === 'asc' ? 1 : -1;
      return 0;
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
      td.textContent = row[field] || '';
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}


let currentData = [];
let currentSort = { column: null, direction: 'asc' };

document.getElementById('filter').addEventListener('change', () => {
  const selected = document.getElementById('filter').value;
  renderTable(currentData, selected);
});

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

    const filter = document.getElementById('filter')?.value || 'all';
    renderTable(currentData, filter);
  });
});

// Basic search filter
document.getElementById('filterInput').addEventListener('input', function () {
  const filter = this.value.toLowerCase();
  const rows = document.querySelectorAll('#dataTable tbody tr');
  rows.forEach(row => {
    row.style.display = row.innerText.toLowerCase().includes(filter) ? '' : 'none';
  });
});

loadData();
