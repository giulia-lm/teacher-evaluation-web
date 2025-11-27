// fetch-utils.js
export async function fetchWithErrors(url, opts = {}) {
  const resp = await fetch(url, opts);
  if (!resp.ok) {
    // intentar parsear JSON
    let body = null;
    try {
      body = await resp.json();
    } catch (e) {
      // no JSON -> leer texto
      try { body = await resp.text(); } catch (e) { body = null; }
    }
    // si es error de BD o service unavailable
    if (resp.status === 503 && body && body.error === 'db_unavailable') {
      showErrorPopup('No es posible conectar con la base de datos. Intenta más tarde.');
      throw new Error('DB_UNAVAILABLE');
    }
    // mensajes genéricos
    const msg = (body && (body.message || body.error)) || `Error ${resp.status}`;
    showErrorPopup(msg);
    throw new Error(msg);
  }
  // ok
  return resp.json();
}

// función simple para mostrar popup (puedes reemplazar por tu toast)
function showErrorPopup(msg) {
  // si ya tienes un sistema de toast, úsalo
  if (window.showToast) return window.showToast(msg, {type:'error'});
  alert(msg); // fallback simple
}
