document.addEventListener('DOMContentLoaded', () => {
  const tableBody = document.querySelector('#users-table tbody');

  // modal elements
  const modal = document.getElementById('user-modal');
  const modalTitle = document.getElementById('modal-title');
  const form = document.getElementById('user-form');
  const btnOpenAdd = document.getElementById('btn-open-add');
  const btnCancel = document.getElementById('user-cancel');

  function showModal(mode='create', user={}) {
    modal.style.display = 'block';
    modalTitle.textContent = mode === 'create' ? 'Agregar usuario' : 'Editar usuario';
    document.getElementById('user-id').value = user.id || '';
    document.getElementById('user-name').value = user.name || '';
    document.getElementById('user-matricula').value = user.matricula || '';
    document.getElementById('user-role').value = user.role || 'alumnx';
    document.getElementById('user-password').value = ''; // siempre vacío
  }
  function hideModal() {
    modal.style.display = 'none';
  }
  btnOpenAdd.addEventListener('click', () => showModal('create'));
  btnCancel.addEventListener('click', hideModal);

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const id = document.getElementById('user-id').value;
    const payload = {
      id: id || undefined,
      name: document.getElementById('user-name').value.trim(),
      matricula: document.getElementById('user-matricula').value.trim(),
      role: document.getElementById('user-role').value,
      password: document.getElementById('user-password').value
    };
    try {
      const url = id ? '/admin/api/user-update' : '/admin/api/user-create';
      const resp = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
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
    if (!confirm('¿Seguro que quieres eliminar al usuario #' + id + '?')) return;
    try {
      const resp = await fetch('/admin/api/user-delete', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id})
      });
      const data = await resp.json();
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
      const resp = await fetch('/admin/api/users-all', { credentials: 'same-origin' });
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
        tr.innerHTML = `
          <td>${u.id ?? ''}</td>
          <td>${u.name ?? ''}</td>
          <td>${u.matricula ?? ''}</td>
          <td>${u.role ?? ''}</td>
          <td>${u.created_at ?? ''}</td>
          <td>
            <button class="btn-edit" data-id="${u.id}">Editar</button>
            <button class="btn-delete" data-id="${u.id}">Borrar</button>
          </td>
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

  loadAllUsers();
  document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('user-modal');
  const openBtn = document.getElementById('btn-open-add');
  const cancelBtn = document.getElementById('user-cancel');

  openBtn.addEventListener('click', () => {
    modal.classList.add('show');
  });

  cancelBtn.addEventListener('click', () => {
    modal.classList.remove('show');
  });

  // Cierra el modal al hacer clic fuera del contenido
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.remove('show');
  });
});

});
