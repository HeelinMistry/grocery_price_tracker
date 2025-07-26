const jsonFilePath = 'data/latest.json'; // Or dynamically get latest if needed

async function loadData() {
  const response = await fetch(jsonFilePath);
  const data = await response.json();

  const tbody = document.querySelector('#dataTable tbody');
  tbody.innerHTML = '';

  data.forEach(row => {
    const tr = document.createElement('tr');

    // Add class if there's an old_price value
    if (row.old_price) {
      tr.classList.add('has-old-price');
    }

    // Add class if there's a promotion
    if (row.promotion) {
      tr.classList.add('has-promo');
    }

    // Add classes if there's a promotion and old price
    if (row.promotion && row.old_price) {
      tr.classList.add('has-old-price', 'has-promo');
    }

    ['store', 'name', 'price', 'old_price', 'promotion'].forEach(field => {
      const td = document.createElement('td');
      td.textContent = row[field] || '';
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}

// Basic search filter
document.getElementById('filterInput').addEventListener('input', function () {
  const filter = this.value.toLowerCase();
  const rows = document.querySelectorAll('#dataTable tbody tr');
  rows.forEach(row => {
    row.style.display = row.innerText.toLowerCase().includes(filter) ? '' : 'none';
  });
});

loadData();
