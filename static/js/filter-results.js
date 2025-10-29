document.getElementById('first-filter').addEventListener('change', async function() {
  const value = this.value;
  if (!value) return;

  // Petición AJAX al backend
  const response = await fetch('/teachers/inicio-teachers', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ first_filter: value })
  });

  const data = await response.json();
  const secondSelect = document.getElementById('second-filter');
  const secondForm = document.getElementById('second-form');
  const filterTypeInput = document.getElementById('filter-type');

  // Guardar el tipo de filtro
  filterTypeInput.value = value;

  secondSelect.innerHTML = '';

  data.results.forEach(item => {
    const opt = document.createElement('option');
    const label = item.materia || item.grupo || 'Sin nombre';
    opt.textContent = label;
    opt.value = item.id;
    secondSelect.appendChild(opt);
  });

  secondForm.style.display = 'block';
});
