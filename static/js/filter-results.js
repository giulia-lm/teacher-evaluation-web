document.addEventListener('DOMContentLoaded', () => {
  const firstFilter = document.getElementById('first-filter');
  const secondSelect = document.getElementById('second-filter');
  const secondForm = document.getElementById('second-form');
  const filterTypeInput = document.getElementById('filter-type');

  // fallback: si la template no inyectó RESULTS_ENDPOINT
  const endpoint = (typeof RESULTS_ENDPOINT !== 'undefined' && RESULTS_ENDPOINT) ? RESULTS_ENDPOINT : window.location.pathname;

  function prepareSecondSelect() {
    secondSelect.innerHTML = '<option value="">Selecciona...</option>';
  }

  prepareSecondSelect();
  secondForm.style.display = 'none';

  firstFilter.addEventListener('change', async function() {
    const value = this.value;
    if (!value) {
      secondForm.style.display = 'none';
      prepareSecondSelect();
      filterTypeInput.value = '';
      return;
    }

    filterTypeInput.value = value;
    prepareSecondSelect();
    secondForm.style.display = 'block';

    try {
      const resp = await fetch(endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ first_filter: value })
      });

      if (!resp.ok) {
        // mostrar en consola y en el select
        console.error('Fetch POST falló con status', resp.status);
        prepareSecondSelect();
        const errOpt = document.createElement('option');
        errOpt.value = '';
        errOpt.textContent = 'Error al cargar opciones';
        secondSelect.appendChild(errOpt);
        return;
      }

      const data = await resp.json().catch(() => ({ results: [] }));
      const rows = Array.isArray(data.results) ? data.results : [];

      if (rows.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'No hay opciones disponibles';
        secondSelect.appendChild(opt);
      } else {
        rows.forEach(item => {
          const opt = document.createElement('option');
          const label = item.label || item.materia || item.grupo || item.name || 'Sin nombre';
          opt.textContent = label;
          opt.value = item.id;
          secondSelect.appendChild(opt);
        });
      }
      secondSelect.focus();
    } catch (err) {
      console.error('Error cargando opciones (JS):', err);
      prepareSecondSelect();
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'Error al cargar opciones';
      secondSelect.appendChild(opt);
    }
      // asegurarnos que antes de submit exista el filter-type
  secondForm.addEventListener('submit', (ev) => {
    // si no hay tipo, prevenir submit
    if (!filterTypeInput.value) {
      ev.preventDefault();
      alert('Selecciona primero el tipo de filtro (Materia/Grupo).');
      return false;
    }
    // si no hay seleccionado en secondSelect, permitir submit igualmente (el backend devolverá vacío)
    return true;
  });
});
  });
