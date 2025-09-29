// static/js/main.js
window.initFormNuevoCliente = function(container) {
    if (!container) container = document;
    const form = container.querySelector('#form-nuevo-cliente');
    if (!form) { console.log('initFormNuevoCliente: form no encontrado'); return; }
    if (form.dataset._ajaxBound) { console.log('initFormNuevoCliente: ya binded'); return; }
    form.dataset._ajaxBound = '1';
    console.log('initFormNuevoCliente: bind submit AJAX');
  
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      console.log('initFormNuevoCliente: submit interceptado');
      const btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.innerText = 'Guardando...';