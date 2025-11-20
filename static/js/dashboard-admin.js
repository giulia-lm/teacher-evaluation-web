document.addEventListener('DOMContentLoaded', () => {
  const tableBody = document.querySelector('#users-table tbody');

  // modal elements (si usas modal)
  const modal = document.getElementById('user-modal');
  const modalTitle = document.getElementById('modal-title');
  const form = document.getElementById('user-form');
  const btnOpenAdd = document.getElementById('btn-open-add');
  const btnCancel = document.getElementById('user-cancel');

  // filtros y botones (asegúrate que existen en el HTML)
  const filtroRol = document.getElementById('filtro-rol');
  const filtroCreado = document.getElementById('filtro-creado');
  const btnFiltrar = document.getElementById('btn-filtrar-users');
  const btnReset = document.getElementById('btn-reset-users');
  


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

const roleSelect = document.getElementById('user-role');
const alumnxDiv   = document.getElementById('alumnx-options');
const docenteDiv  = document.getElementById('docente-options');



roleSelect.addEventListener('change', () => {
  const role = roleSelect.value;

  if (role === 'alumnx') {
    alumnxDiv.style.display = 'block';
    docenteDiv.style.display = 'none';
  } 
  else if (role === 'docente') {
    alumnxDiv.style.display = 'none';
    docenteDiv.style.display = 'block';
  } 
  else {
    alumnxDiv.style.display = 'none';
    docenteDiv.style.display = 'none';
  }
});

function showModal(mode='create', user={}) {
    modal.style.display = 'block';
    modalTitle.textContent = mode === 'create' ? 'Agregar usuario' : 'Editar usuario';

    document.getElementById('user-id').value = user.id || '';
    document.getElementById('user-name').value = user.name || '';
    document.getElementById('user-matricula').value = user.matricula || '';

    // Reset de selects
    document.getElementById('alumnx-grupo').value = user.alumnx_grupo || '';
    if (user.docente_materias) {
      document.querySelectorAll('input[name="docente_materias"]').forEach(cb => {
        cb.checked = user.docente_materias.includes(parseInt(cb.value));
      });
    } else {
      document.querySelectorAll('input[name="docente_materias"]').forEach(cb => cb.checked = false);
    }

    roleSelect.disabled = (mode === 'edit');

    // Forzar cambio visual según rol
    roleSelect.value = user.role || 'alumnx';
    roleSelect.dispatchEvent(new Event('change'));

    document.getElementById('user-password').value = '';
}

  function hideModal() {
    modal.style.display = 'none';
  }

  btnOpenAdd.addEventListener('click', () => showModal('create'));
  btnCancel.addEventListener('click', hideModal);

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();

    const id = document.getElementById('user-id').value;
    const materias = Array.from(
      document.querySelectorAll('input[name="docente_materias"]:checked')
    ).map(cb => parseInt(cb.value));

    const payload = {
      id: document.getElementById('user-id').value || undefined,
      name: document.getElementById('user-name').value.trim(),
      matricula: document.getElementById('user-matricula').value.trim(),
      role: document.getElementById('user-role').value,
      password: document.getElementById('user-password').value,
    };

    if (payload.role === "docente") {
      payload.docente_materias = materias;   
    } 


    if (payload.role === "alumnx") {
      payload.alumnx_grupo = parseInt(document.getElementById("alumnx-grupo").value);
    }
    try {
      const url = id ? '/admin/api/user-update' : '/admin/api/user-create';
      const resp = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (resp.ok) {
        if(url.search('update')){
          showToast("Usuario editado correctamente");
        }else if(url.search('create')){
          showToast("Usuario creado correctamente");
        }    
        loadAllUsers();
      }
      if (!resp.ok) {
        console.error('Error server:', data);
        alert('Error: ' + (data.error || resp.status));
        return;
      }
      hideModal();
      // si viene user en data, reusar; si no, recargar la lista
      await loadAllUsers();
    } catch (err) {
      console.error('Error guardando usuario:', err);
      alert('Error de conexión');
    }
  });

  // BORRAR con confirmación
  async function deleteUser(id) {
    const ok = await toastConfirm('¿Seguro que quieres eliminar al usuario #' + id + '?');
    if (!ok) return;
    try {
      const resp = await fetch('/admin/api/user-delete', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id})
      });
      const data = await resp.json();
      if (resp.ok) {
        showToast("Usuario eliminado correctamente");
        loadAllUsers();
      }
      if (!resp.ok) {
        console.error('Error delete:', data);
        alert('No se pudo borrar: ' + (data.error || resp.status));
        return;
      }
      await loadAllUsers();
    } catch (err) {
      console.error('Error borrando:', err);
      alert('Error de conexión');
    }
  }

  async function loadAllUsers() {
    
    try {
      
      const params = new URLSearchParams();

      const roleVal = (filtroRol && filtroRol.value) || '';
      const dateVal = (filtroCreado && filtroCreado.value) || ''; // formato "YYYY-MM"

      if (roleVal) params.set('role', roleVal);
      if (dateVal) params.set('date', dateVal);


      const url = '/admin/api/users-all' + (params.toString() ? ('?' + params.toString()) : '');
      const resp = await fetch(url, { credentials: 'same-origin' });

      if (!resp.ok) {
        const txt = await resp.text();
        tableBody.innerHTML = `<tr><td colspan="6">Error: ${resp.status}</td></tr>`;
        console.error('fetch failed', resp.status, txt);
        return;
      }
      const users = await resp.json();
      tableBody.innerHTML = '';
      if (!Array.isArray(users) || users.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="6">No hay usuarios</td></tr>`;
        return;
      }

      
      users.forEach(u => {
        const tr = document.createElement('tr');

        // fecha en español
        let fecha = "";
        if (u.created_at) {
          const d = new Date(u.created_at);
          if (!isNaN(d)) {
            fecha = d.toLocaleString("es-MX", {
              timeZone: "America/Mexico_City",
              year: "numeric",
              month: "long",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit"
            });
          } else {
            fecha = u.created_at;
          }
        }
        // -------------------------------------
        const acciones = u.role === 'admin'
        ? `<button class="btn-edit" data-id="${u.id}">Editar</button>`
        : `
            <button class="btn-edit" data-id="${u.id}">Editar</button>
            <button class="btn-delete" data-id="${u.id}">Borrar</button>
          `;


        tr.innerHTML = `
          <td>${u.id ?? ''}</td>
          <td>${u.name ?? ''}</td>
          <td>${u.matricula ?? ''}</td>
          <td>${u.role ?? ''}</td>
          <td>${fecha}</td>
          <td>${acciones}</td>
        `;
        tableBody.appendChild(tr);
    });

      // attach handlers
      document.querySelectorAll('.btn-edit').forEach(b => {
        b.addEventListener('click', async (ev) => {
          const id = b.dataset.id;
          // obtener datos del usuario (o extraer de fila)
          const row = b.closest('tr');
          const user = {
            id,
            name: row.children[1].textContent,
            matricula: row.children[2].textContent,
            role: row.children[3].textContent
          };
          showModal('edit', user);
        });
      });
      document.querySelectorAll('.btn-delete').forEach(b => {
        b.addEventListener('click', (ev) => deleteUser(b.dataset.id));
      });

    } catch (err) {
      console.error('Error fetch:', err);
      tableBody.innerHTML = `<tr><td colspan="6">Error al conectar con el servidor</td></tr>`;
    }
  }

  // Event listeners para filtros
  if (btnFiltrar) {
    btnFiltrar.addEventListener('click', (e) => {
      e.preventDefault();
      loadAllUsers();
    });
  } else {
    console.warn('btnFiltrar no encontrado en DOM');
  }

  if (btnReset) {
    btnReset.addEventListener('click', (e) => {
      e.preventDefault();
      if (filtroRol) filtroRol.value = '';
      if (filtroCreado) filtroCreado.value = '';
      loadAllUsers();
    });
  } else {
    console.warn('btnReset no encontrado en DOM');
  }

  // modal open/close si existen botones
  if (btnOpenAdd && modal) {
    btnOpenAdd.addEventListener('click', () => modal.classList.add('show'));
  }
  if (btnCancel && modal) {
    btnCancel.addEventListener('click', () => modal.classList.remove('show'));
  }
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('show');
    });
  }

  // primera carga
  loadAllUsers();
});