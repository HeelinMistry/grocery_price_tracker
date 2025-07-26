const jsonFilePath = 'data/latest.json'; // Or dynamically get latest if needed

async function loadData() {
  const response = await fetch(jsonFilePath);
  const data = await response.json();

  const tbody = document.querySelector('#dataTable tbody');
  tbody.innerHTML = '';

  data.forEach(row => {
    const tr = document.createElement('tr');
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
