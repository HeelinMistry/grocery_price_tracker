const jsonFilePath = 'data/latest.json'; // Or dynamically get latest if needed

async function loadData(filter = 'all') {
  const response = await fetch(jsonFilePath);
  const data = await response.json();
  renderTable(data, filter);
}

function renderTable(data, filter = 'all') {
  const tbody = document.querySelector('#dataTable tbody');
  tbody.innerHTML = '';

  data.forEach(row => {
    const hasOldPrice = row.old_price && row.old_price !== '';
    const hasPromo = row.promotion && row.promotion !== '';

    // Filter logic
    if (
      (filter === 'old_price' && !hasOldPrice) ||
      (filter === 'promotion' && !hasPromo) ||
      (filter === 'both' && !(hasOldPrice && hasPromo))
    ) {
      return; // Skip rows that don't match filter
    }

    const tr = document.createElement('tr');

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

document.getElementById('filter').addEventListener('change', (e) => {
  loadData(e.target.value);
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
