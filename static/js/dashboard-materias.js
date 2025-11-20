document.addEventListener('DOMContentLoaded', () => {

  const tbody = document.querySelector('#materias-table tbody');


  // modal elements
  const modal = document.getElementById('materia-modal');
  const modalTitle = document.getElementById('modal-title');
  const form = document.getElementById('materia-form');
  const btnOpenAdd = document.getElementById('btn-add-materia');
  const btnCancel = document.getElementById('materia-cancel');

  function showToast(msg) {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.classList.add("toast");
    toast.textContent = msg;
    container.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 5000); 
  }
  function toastConfirm(message) {
  return new Promise((resolve) => {
    const container = document.getElementById("toast-container");

    const toast = document.createElement("div");
    toast.classList.add("toast-confirm");

    toast.innerHTML = `
      <div>${message}</div>
      <div class="toast-confirm-buttons">
        <button class="toast-btn toast-no">Cancelar</button>
        <button class="toast-btn toast-yes">Eliminar</button>
      </div>
    `;

    container.appendChild(toast);

    toast.querySelector(".toast-yes").onclick = () => {
      toast.remove();
      resolve(true);
    };

    toast.querySelector(".toast-no").onclick = () => {
      toast.remove();
      resolve(false);
    };
  });
}



function showModal(mode='create', materia={}) {
    modal.style.display = 'block';
    modalTitle.textContent = mode === 'Agregar materia';

    document.getElementById('materia-id').value = materia.id || '';
    document.getElementById('materia-name').value = materia.name || '';
    document.getElementById('docente-materia').value = materia.docente || '';
    document.getElementById('grupo').value = materia.grupo || '';
}

  function hideModal() {
    modal.style.display = 'none';
  }

  btnOpenAdd.addEventListener('click', () => showModal('create'));
  btnCancel.addEventListener('click', hideModal);

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();

    const id = document.getElementById('materia-id').value;

    const payload = {
      id: document.getElementById('materia-id').value || undefined,
      name: document.getElementById('materia-name').value.trim(),
      docente: document.getElementById('docente-materia').value.trim(),
      grupo:  document.getElementById('grupo').value.trim()
    };


    try {
      const url = '/admin/api/materia-create';
      const resp = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (resp.ok) {
        if(url.search('create')){
          showToast("Materia creada correctamente");
        }    
        loadMaterias();
      }
      if (!resp.ok) {
        console.error('Error server:', data);
        alert('Error: ' + (data.error || resp.status));
        return;
      }
      hideModal();
      // si viene user en data, reusar; si no, recargar la lista
      await loadMaterias();
    } catch (err) {
      console.error('Error guardando materia:', err);
      alert('Error de conexión');
    }
  });


  async function loadMaterias() {
    try {
      const resp = await fetch('/admin/api/materias', { credentials: 'same-origin' });
      if (!resp.ok) {
        const txt = await resp.text();
        console.error('Respuesta /admin/api/respuestas fallo:', resp.status, txt);
        tbody.innerHTML = `<tr><td colspan="6">Error ${resp.status}</td></tr>`;
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
