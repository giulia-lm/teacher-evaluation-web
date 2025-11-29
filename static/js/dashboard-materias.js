document.addEventListener('DOMContentLoaded', () => {

  const tbody = document.querySelector('#materias-table tbody');


  // modal elements
  const modal = document.getElementById('materia-modal');
  const modalTitle = document.getElementById('materia-modal-title');
  const form = document.getElementById('materia-form');
  const btnOpenAdd = document.getElementById('btn-add-materia');
  const btnCancel = document.getElementById('materia-cancel');

  const filtroGrupo = document.getElementById('filtro-grupo');
  const filtroDocente = document.getElementById('filtro-docente');
  const btnFiltrar = document.getElementById('btn-filtrar-materias');
  const btnReset = document.getElementById('btn-reset-materias');


let activeToast = null;

function showToast(msg) {

  const container = document.getElementById("toast-container");

  // Si ya hay un toast, no crear otro
  if (activeToast) return;

  const toast = document.createElement("div");
  toast.classList.add("toast");
  toast.textContent = msg;

  container.appendChild(toast);
  activeToast = toast;

  setTimeout(() => {
    toast.remove();
    activeToast = null;
  }, 1000);
}


  function toastConfirm(message) {
  return new Promise((resolve) => {
    const container = document.getElementById("toast-container");
    if (activeToast) return;

    const toast = document.createElement("div");
    toast.classList.add("toast-confirm");

    toast.innerHTML = `
      <div>${message}</div>
      <div class="toast-confirm-buttons">
        <button class="toast-btn toast-no">Cancelar</button>
        <button class="toast-btn toast-yes">Eliminar</button>
      </div>
    `;

    activeToast = toast;
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


function showModalMateria(mode='create', materia={}) {
    modal.style.display = 'block';
    modalTitle.textContent = mode === 'create' ? 'Agregar materia' : 'Editar materia';


    document.getElementById('materia-id').value = materia.id || '';
    document.getElementById('materia-name').value = materia.name || '';
    document.getElementById('docente-materia').value = materia.id_docente || '';
    document.getElementById('grupo').value = materia.id_grupo || '';
}


  function hideModal() {
    modal.style.display = 'none';
  }

  btnOpenAdd.addEventListener('click', () => showModalMateria('create'));
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
      const url = id ? '/admin/api/materia-update' : '/admin/api/materia-create';

      const resp = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });      const data = await resp.json();
      if (resp.ok) {
        if(url.includes('update')){
          showToast("Materia editada correctamente");
        }else if(url.includes('create')){
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


  async function deleteMateria(id) {
    const ok = await toastConfirm('¿Seguro que quieres eliminar la materia #' + id + '?');
    if (!ok) return;
    try {
      const resp = await fetch('/admin/api/materia-delete', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id})
      });
      const data = await resp.json();
      if (resp.ok) {
        showToast("Materia eliminada correctamente");
        loadMaterias();
      }
      if (!resp.ok) {
        console.error('Error delete:', data);
        alert('No se pudo borrar: ' + (data.error || resp.status));
        return;
      }
      await loadMaterias();
    } catch (err) {
      console.error('Error borrando:', err);
      alert('Error de conexión');
    }
  }

  async function loadMaterias() {
    try {

      const params = new URLSearchParams();

      const grupoVal = (filtroGrupo && filtroGrupo.value) || '';
      const docenteVal = (filtroDocente && filtroDocente.value) || ''; 

      if (grupoVal) params.set('grupo', grupoVal);
      if (docenteVal) params.set('docente', docenteVal);


      const url = '/admin/api/materias' + (params.toString() ? ('?' + params.toString()) : '');
      const resp = await fetch(url, { credentials: 'same-origin' });


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

        const acciones = `
            <button class="btn-materia-edit" data-id="${m.id}">Editar</button>
            <button class="btn-materia-delete" data-id="${m.id}">Borrar</button>
          `;

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${m.id}</td>
          <td>${m.name}</td>
          <td>${docentesText}</td>
          <td>${gruposText}</td>
          <td>${acciones}</td>
        `;
        tbody.appendChild(tr);
      });


      document.querySelectorAll('.btn-materia-edit').forEach(b => {
        b.addEventListener('click', async (ev) => {
          const id = b.dataset.id;
          // obtener datos de la materia (o extraer de fila)
          const row = b.closest('tr');
          const materia = {
            id,
            name: row.children[1].textContent,
            id_docente: row.children[2].textContent,
            id_grupo: row.children[3].textContent
          };
          showModalMateria('edit', materia);
        });
      });
      document.querySelectorAll('.btn-materia-delete').forEach(b => {
        b.addEventListener('click', (ev) => deleteMateria(b.dataset.id));
      });

    } catch (err) {
      console.error('Error cargando materias:', err);
      tbody.innerHTML = `<tr><td colspan="4">Error al conectar</td></tr>`;
    }
  }

if (btnFiltrar) {
    btnFiltrar.addEventListener('click', (e) => {
      e.preventDefault();
      loadMaterias();
    });
  } else {
    console.warn('btnFiltrar (materias) no encontrado en DOM');
  }

  if (btnReset) {
    btnReset.addEventListener('click', (e) => {
      e.preventDefault();
      if (filtroGrupo) filtroGrupo.value = '';
      if (filtroDocente) filtroDocente.value = '';
      loadMaterias();
    });
  } else {
    console.warn('btnReset (materias) no encontrado en DOM');
  }



  loadMaterias();
});
