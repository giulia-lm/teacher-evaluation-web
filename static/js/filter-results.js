
  document.getElementById('first-filter').addEventListener('change', async function() {
    const value = this.value;
    if (!value) return;

    // Petición AJAX al backend para no recargar la página
    const response = await fetch('/teachers/inicio-teachers', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ first_filter: value })
    });

    const data = await response.json(); //  JSON del backend
    const secondSelect = document.getElementById('second-filter');
    const secondForm = document.getElementById('second-form');

    secondSelect.innerHTML = '';

    // Agregar nuevas opciones
    data.results.forEach(option => {
      const opt = document.createElement('option');
      opt.textContent = option;
      opt.value = option;
      secondSelect.appendChild(opt);
    });

    // Mostrar el segundo select
    secondForm.style.display = 'block';
  });
