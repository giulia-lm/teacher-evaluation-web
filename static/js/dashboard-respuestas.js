document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.querySelector('#responses-table tbody');


  const filtroForm= document.getElementById('filtro-form');
  const filtroAlumnx = document.getElementById('filtro-alumnx');
  const filtroFecha = document.getElementById('filtro-fecha');
  const btnFiltrar = document.getElementById('btn-filtrar-respuestas');
  const btnReset = document.getElementById('btn-reset-respuestas');

  async function loadResponses() {
    try {

      const params = new URLSearchParams();

      const formVal = (filtroForm && filtroForm.value) || '';
      const alumnxVal = (filtroAlumnx && filtroAlumnx.value) || ''; 
      const fechaVal = (filtroFecha && filtroFecha.value) || '';

      if (formVal) params.set('form', formVal);
      if (alumnxVal) params.set('alumnx', alumnxVal);
      if (fechaVal) params.set('date', fechaVal);


      params.set('format', 'json');

      const url = '/admin/api/respuestas' + (params.toString() ? ('?' + params.toString()) : '');
      console.debug('loadResponses -> URL:', url);

      const resp = await fetch(url, { credentials: 'same-origin' });

      //const resp = await fetch('/admin/api/respuestas?format=json', { credentials: 'same-origin' });
      if (!resp.ok) {
      const txt = await resp.text();
      console.error('Respuesta /admin/api/respuestas fallo:', resp.status, txt);
      tbody.innerHTML = `<tr><td colspan="6">Error ${resp.status}</td></tr>`;
      return;
    }

      const data = await resp.json();
      console.log('Respuestas (backend):', data);

      tbody.innerHTML = '';

      if (!Array.isArray(data) || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6">No hay respuestas registradas</td></tr>`;
        return;
      }

      data.forEach(r => {
        // campos en top-level: tratamos varias posibilidades
        //const responseId = r.response_id ?? r.id ?? '';
        //const formId = r.form_id ?? r.id_form ?? r.idForm ?? '';
        const formTitle = r.form_title ?? r.title ?? r.formTitle ?? '';
        //const alumnxId = r.alumnx_id ?? r.id_alumnx ?? '';
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
        let fecha = "";
        if (submitted) {
          const date = new Date(submitted);
          fecha = date.toLocaleString("es-MX", {
            timeZone: "America/Mexico_City",
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
          });
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `

          <td>${escapeHtml(String(formTitle))}</td>

          <td>${escapeHtml(String(alumnxName))} ${alumnxMat ? `(${escapeHtml(alumnxMat)})` : ''}</td>
          <td>${escapeHtml(String(fecha))}</td>
          <td>${answersHtml}</td>
        `;
        tbody.appendChild(tr);
      });

    } catch (err) {
      console.error('Error cargando respuestas:', err);
      tbody.innerHTML = `<tr><td colspan="7">Error al conectar con el servidor</td></tr>`;
    }
  }

  if (btnFiltrar) {
    btnFiltrar.addEventListener('click', (e) => {
      e.preventDefault();
      loadResponses();
    });
  } else {
    console.warn('btnFiltrar (respuestas) no encontrado en DOM');
  }

  if (btnReset) {
    btnReset.addEventListener('click', (e) => {
      e.preventDefault();
      if (filtroForm) filtroForm.value = '';
      if (filtroAlumnx) filtroAlumnx.value = '';
      if (filtroFecha) filtroFecha.value = '';
      loadResponses();
    });
  } else {
    console.warn('btnReset (respuestas) no encontrado en DOM');
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
