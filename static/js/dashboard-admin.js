document.addEventListener('DOMContentLoaded', () => {
  const tableBody = document.querySelector('#users-table tbody');

  async function loadAllUsers() {
    try {
      const resp = await fetch('/admin/api/users-all', { credentials: 'same-origin' });
      if (!resp.ok) {
        tableBody.innerHTML = `<tr><td colspan="6">Error: ${resp.status}</td></tr>`;
        console.error('fetch failed', resp.status, resp.statusText);
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
          <td>${u.email ?? ''}</td>
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
