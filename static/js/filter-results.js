document.addEventListener('DOMContentLoaded', () => {
  const firstFilter = document.getElementById('first-filter');
  const secondSelect = document.getElementById('second-filter');
  const secondForm = document.getElementById('second-form');
  const filterTypeInput = document.getElementById('filter-type');

  // helper: limpia y coloca placeholder
  function prepareSecondSelect() {
    secondSelect.innerHTML = '<option value="">Selecciona...</option>';
  }

  prepareSecondSelect();
  secondForm.style.display = 'none';

  firstFilter.addEventListener('change', async function() {
    const value = this.value;
    // ocultar si no hay opción seleccionada
    if (!value) {
      secondForm.style.display = 'none';
      prepareSecondSelect();
      filterTypeInput.value = '';
      return;
    }

    // Guardar el tipo de filtro (se envía luego con el GET)
    filterTypeInput.value = value;

    // Petición AJAX al backend (usa la misma ruta de la página para evitar hardcode)
    try {
      const resp = await fetch(window.location.pathname, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ first_filter: value })
      });

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const data = await resp.json();
      const rows = data.results || [];

      // poblar segundo select
      prepareSecondSelect();
      if (rows.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'No hay opciones disponibles';
        secondSelect.appendChild(opt);
      } else {
        rows.forEach(item => {
          const opt = document.createElement('option');
          // compatibilidad con ambos formatos: {id,label} o {id, materia} / {id, grupo}
          const label = item.label || item.materia || item.grupo || item.name || 'Sin nombre';
          opt.textContent = label;
          opt.value = item.id;
          secondSelect.appendChild(opt);
        });
      }

      secondForm.style.display = 'block';
      secondSelect.focus();
    } catch (err) {
      console.error('Error cargando opciones:', err);
      // mostrar mensaje simple en el select
      prepareSecondSelect();
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'Error al cargar opciones';
      secondSelect.appendChild(opt);
      secondForm.style.display = 'block';
    }
  });
});
