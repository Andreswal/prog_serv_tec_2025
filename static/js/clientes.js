// static/js/clientes.js
(function () {
    /**
     * Inicializa buscador y selección de clientes dentro de un contenedor.
     * @param {HTMLElement} container - El nodo donde está la tabla de clientes.
     */
    function initClientes(container) {
        container = container || document;

        const input = container.querySelector('#busquedaCliente');
        const tabla = container.querySelector('#tabla-clientes');
        if (!input || !tabla) {
            console.warn('clientesInit: no se encontró input o tabla en el contenedor');
            return;
        }

        let filas = Array.from(tabla.querySelectorAll('tbody tr.fila-cliente'));
        const sinCoincidencias = container.querySelector('#sin-coincidencias');

        // --- Filtro de búsqueda ---
        function actualizarFilas() {
            const filtro = input.value.trim().toLowerCase();
            let visibles = 0;
            filas.forEach(row => {
                const texto = row.textContent.toLowerCase();
                const ok = filtro === '' ? true : texto.includes(filtro);
                row.style.display = ok ? '' : 'none';
                if (ok) visibles++;
                row.classList.remove('resaltado');
            });
            if (sinCoincidencias) {
                sinCoincidencias.style.display = visibles === 0 ? '' : 'none';
            }
        }

        // Evitar listeners duplicados
        if (input.__clientes_listener) {
            input.removeEventListener('input', input.__clientes_listener);
        }
        input.__clientes_listener = actualizarFilas;
        input.addEventListener('input', actualizarFilas, { passive: true });

        // --- Selección de filas ---
        filas.forEach(row => {
            if (row.__clientes_click_handler) {
                row.removeEventListener('click', row.__clientes_click_handler);
            }
            const handler = function () {
                filas.forEach(r => r.classList.remove('resaltado'));
                row.classList.add('resaltado');

                const cliente = {
                    nombre: row.dataset.nombre || '',
                    telefono: row.dataset.telefono || '',
                    email: row.dataset.email || '',
                    direccion: row.dataset.direccion || '',
                    localidad: row.dataset.localidad || '',
                    provincia: row.dataset.provincia || '',
                    comentarios: row.dataset.comentarios || ''
                };

                try {
                    if (window.parent && window.parent !== window) {
                        window.parent.postMessage({ cliente }, '*');
                    } else {
                        window.postMessage({ cliente }, '*');
                    }
                } catch (e) {
                    console.warn('clientesInit: postMessage falló', e);
                }
            };
            row.__clientes_click_handler = handler;
            row.addEventListener('click', handler);
        });

        // Ejecutar filtro inicial
        actualizarFilas();
        console.log('clientesInit ejecutado en', container);
    }

    // Exponer globalmente
    window.clientesInit = initClientes;

    // También escuchar evento personalizado
    document.addEventListener('clientes:rendered', function (e) {
        const container = e && e.detail && e.detail.container ? e.detail.container : document;
        initClientes(container);
    });
})();
