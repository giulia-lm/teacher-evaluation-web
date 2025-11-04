document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.querySelector('#materias-table tbody');

  async function loadMaterias() {
    try {
      const resp = await fetch('/admin/api/materias', { credentials: 'same-origin' });
      if (!resp.ok) {
        tbody.innerHTML = `<tr><td colspan="4">Error ${resp.status}</td></tr>`;
        return;
      }
      const materias = await resp.json();
      tbody.innerHTML = '';
      if (!materias.length) {
        tbody.innerHTML = `<tr><td colspan="4">No hay materias</td></tr>`;
        return;
      }

      materias.forEach(m => {
        const docentesText = m.docentes.map(d => `${d.name} (${d.matricula || '—'})`).join('<br>') || 'Sin docente';
        const gruposText = m.grupos.map(g => g.nombre).join(', ') || 'Sin grupos';

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${m.id}</td>
          <td>${m.name}</td>
          <td>${docentesText}</td>
          <td>${gruposText}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      console.error('Error cargando materias:', err);
      tbody.innerHTML = `<tr><td colspan="4">Error al conectar</td></tr>`;
    }
  }

  loadMaterias();
});
