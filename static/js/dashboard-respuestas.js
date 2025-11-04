document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.querySelector('#responses-table tbody');

  async function loadResponses() {
    try {
      const resp = await fetch('/admin/api/respuestas?format=json', { credentials: 'same-origin' });
      if (!resp.ok) {
        tbody.innerHTML = `<tr><td colspan="6">Error ${resp.status}</td></tr>`;
        return;
      }

      const data = await resp.json();
      console.log('Respuestas (backend):', data); // <-- útil para debug

      tbody.innerHTML = '';

      if (!Array.isArray(data) || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6">No hay respuestas registradas</td></tr>`;
        return;
      }

      data.forEach(r => {
        // campos en top-level: tratamos varias posibilidades
        const responseId = r.response_id ?? r.id ?? '';
        const formId = r.form_id ?? r.id_form ?? r.idForm ?? '';
        const formTitle = r.form_title ?? r.title ?? r.formTitle ?? '';
        const alumnxId = r.alumnx_id ?? r.id_alumnx ?? '';
        const alumnxName = r.alumnx_name ?? r.name ?? '';
        const alumnxMat = r.alumnx_matricula ?? r.alumnx_matricula ?? '';

        // preparar texto con las answers: pregunta -> (choice_text | texto_respuesta)
        const answers = Array.isArray(r.answers) ? r.answers : [];
        const answersHtml = answers.map(a => {
          const qText = a.question_text ?? a.texto_pregunta ?? a.question_texto ?? 'Pregunta';
          // preferimos choice_text, si no existe usamos texto_respuesta
          const choice = a.choice_text ?? a.texto_respuesta ?? a.choice ?? '';
          // si la pregunta es de tipo open, mostrar texto_respuesta
          return `<strong>${escapeHtml(qText)}</strong>: ${escapeHtml(String(choice || '—'))}`;
        }).join('<br>');

        const submitted = r.submitted_at ?? r.submittedAt ?? '';

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${escapeHtml(String(responseId))}</td>
          <td>${escapeHtml(String(formId))}</td>
          <td>${escapeHtml(String(formTitle))}</td>
          <td>${escapeHtml(String(alumnxId))}</td>
          <td>${escapeHtml(String(alumnxName))} ${alumnxMat ? `(${escapeHtml(alumnxMat)})` : ''}</td>
          <td>${escapeHtml(String(submitted))}</td>
          <td>${answersHtml}</td>
        `;
        tbody.appendChild(tr);
      });

    } catch (err) {
      console.error('Error cargando respuestas:', err);
      tbody.innerHTML = `<tr><td colspan="7">Error al conectar con el servidor</td></tr>`;
    }
  }

  // pequeña función para evitar XSS al inyectar texto
  function escapeHtml(str) {
    return str
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  loadResponses();
});
