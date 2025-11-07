document.addEventListener('DOMContentLoaded', () => {
  const tableBody = document.querySelector('#users-table tbody');

  async function loadAllUsers() {
    try {
      const resp = await fetch('/admin/api/users-all', { credentials: 'same-origin' });
      if (!resp.ok) {
        const txt = await resp.text();
        console.error('Respuesta /admin/api/respuestas fallo:', resp.status, txt);
        tbody.innerHTML = `<tr><td colspan="6">Error ${resp.status}</td></tr>`;
        return;
      }

      const users = await resp.json();
      console.log('users:', users);

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
        `;
        tableBody.appendChild(tr);
      });
    } catch (err) {
      console.error('Error fetch:', err);
      tableBody.innerHTML = `<tr><td colspan="6">Error al conectar con el servidor</td></tr>`;
    }
  }

  loadAllUsers();
});
