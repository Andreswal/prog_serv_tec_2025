
let estadoVentanas = {};
let zIndexActual = 1000; // z-index base para ventanas

function abrirVentana(id, url) {
    // 1) Si ya existe, traerla al frente
    const ventanaExistente = document.getElementById('ventana-' + id);
    if (ventanaExistente) {
        ventanaExistente.style.zIndex = ++zIndexActual;
        return;
    }

    // 2) Crear ventana y estilos
    const ventana = document.createElement('div');
    ventana.id = 'ventana-' + id;
    ventana.className = 'ventana-flotante'; // 🎯 Clave para el cierre fácil con .closest()

    ventana.style.position = 'fixed';
    ventana.style.top = '60px';
    ventana.style.left = '60px';
    ventana.style.width = '800px';
    ventana.style.height = '500px';
    ventana.style.background = 'white';
    ventana.style.border = '2px solid #444';
    ventana.style.boxShadow = '0 0 10px rgba(0,0,0,0.3)';
    ventana.style.zIndex = ++zIndexActual;
    ventana.style.overflow = 'auto';
    ventana.style.resize = 'both';

    // 3) Barra y contenedor
    ventana.innerHTML = `
        <div class="barra-ventana" style="background: #222; color: white; padding: 5px; cursor: move;">
            <span>${id.toUpperCase()}</span>
            <div style="float: right;">
                <button onclick="alternarMinimizar('${id}')" style="margin-right: 5px;">🗕</button>
                <button onclick="maximizarVentana('${id}')" style="margin-right: 5px;">🗖</button>
                <button onclick="document.getElementById('ventana-${id}').remove()">❌</button>
            </div>
        </div>
        <div id="contenido-ventana-${id}" style="padding: 10px;">Cargando...</div>
    `;

    const escritorio = document.getElementById('escritorio');
    if (!escritorio) {
        console.error("No existe el contenedor #escritorio en el DOM.");
        return;
    }
    escritorio.appendChild(ventana);

    // 4) Cargar contenido con jQuery
    const selectorContenido = `#contenido-ventana-${id}`;
    $(selectorContenido).load(url, function (response, status, xhr) {
        const cont = document.getElementById(`contenido-ventana-${id}`);

        if (status === "error") {
            if (cont) cont.innerHTML = `<div class='text-danger'>Error al cargar contenido (${xhr.status}).</div>`;
            return;
        }
        if (!cont) return;

        // Inicializar buscador/tabla si es la ventana de clientes
        if (id === 'clientes' && typeof window.clientesInit === 'function') {
            try {
                window.clientesInit(cont);
                console.log('ventanas.js: clientesInit ejecutado');
            } catch (err) {
                console.error('ventanas.js: error en clientesInit', err);
            }
        }

        // Si es la ventana de nuevo-cliente, forzar bind del submit AJAX
        if (id === 'nuevo-cliente') {
            const contNuevo = document.getElementById('contenido-ventana-nuevo-cliente');
            if (contNuevo) {
                if (typeof window.initFormNuevoCliente === 'function') {
                    console.log('ventanas.js: llamando initFormNuevoCliente desde load');
                    try {
                        window.initFormNuevoCliente(contNuevo);
                    } catch (err) {
                        console.error('ventanas.js: initFormNuevoCliente lanzó error', err);
                    }
                } else {
                    console.log('ventanas.js: initFormNuevoCliente no definida');
                }
            } else {
                console.log('ventanas.js: contenedor contenido-ventana-nuevo-cliente no encontrado');
            }
        }

        // 🔎 Detección por marcador (compatibilidad adicional)
        try {
            const marker = cont.querySelector && cont.querySelector('#cliente-creado-marker');
            if (marker && marker.dataset && marker.dataset.accion === 'cliente_creado') {
                console.log('ventanas.js: marcador cliente creado detectado');
                // cerrar ventana nuevo-cliente si existe
                const vNuevo = document.getElementById('ventana-nuevo-cliente');
                if (vNuevo) vNuevo.remove();
                // refrescar lista clientes parcial si existe
                const vClientesCont = document.getElementById('contenido-ventana-clientes');
                if (vClientesCont) {
                    $(vClientesCont).load('/ordenes/clientes/parcial/', function (resp2, status2, xhr2) {
                        if (status2 === 'error') {
                            vClientesCont.innerHTML = `<div class='text-danger'>Error al refrescar lista (${xhr2.status}).</div>`;
                            return;
                        }
                        if (typeof window.clientesInit === 'function') {
                            window.clientesInit(vClientesCont);
                        }
                        console.log('ventanas.js: lista de clientes refrescada tras marcador.');
                    });
                }
            }
        } catch (e) {
            console.warn('ventanas.js: error al buscar marcador', e);
        }
    });

    // 5) Movible y z-index al frente
    hacerMovible(ventana);
    ventana.addEventListener('mousedown', () => {
        ventana.style.zIndex = ++zIndexActual;
    });

    // 6) Guardar estado
    estadoVentanas[id] = {
        maximizada: false,
        minimizada: false,
        original: {
            width: ventana.style.width,
            height: ventana.style.height,
            top: ventana.style.top,
            left: ventana.style.left,
            resize: ventana.style.resize
        }
    };
}


function hacerMovible(ventana) {
    const barra = ventana.querySelector('.barra-ventana');
    if (!barra) return;
    let offsetX = 0, offsetY = 0, moviendo = false;

    const onMouseMove = function(e) {
        if (moviendo) {
            ventana.style.left = (e.clientX - offsetX) + 'px';
            ventana.style.top = (e.clientY - offsetY) + 'px';
        }
    };

    const onMouseUp = function() {
        moviendo = false;
    };

    barra.addEventListener('mousedown', function(e) {
        moviendo = true;
        offsetX = e.clientX - ventana.offsetLeft;
        offsetY = e.clientY - ventana.offsetTop;
        ventana.style.zIndex = ++zIndexActual;
    });

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
}

function alternarMinimizar(id) {
    const ventana = document.getElementById('ventana-' + id);
    if (!ventana) return;
    const barraInferior = document.getElementById('barra-inferior');

    if (!estadoVentanas[id]) {
        estadoVentanas[id] = { maximizada: false, minimizada: false, original: {
            width: ventana.style.width,
            height: ventana.style.height,
            top: ventana.style.top,
            left: ventana.style.left,
            resize: ventana.style.resize
        }};
    }

    if (!estadoVentanas[id].minimizada) {
        ventana.style.display = 'none';
        estadoVentanas[id].minimizada = true;

        if (barraInferior) {
            const botonRestaurar = document.createElement('button');
            botonRestaurar.id = 'icono-' + id;
            botonRestaurar.className = 'btn btn-sm btn-outline-dark mr-1';
            botonRestaurar.innerText = id.toUpperCase();
            botonRestaurar.onclick = () => {
                ventana.style.display = 'block';
                estadoVentanas[id].minimizada = false;
                if (barraInferior.contains(botonRestaurar)) barraInferior.removeChild(botonRestaurar);
                ventana.style.zIndex = ++zIndexActual;
            };
            barraInferior.appendChild(botonRestaurar);
        }
    } else {
        ventana.style.display = 'block';
        estadoVentanas[id].minimizada = false;

        const botonRestaurar = document.getElementById('icono-' + id);
        if (botonRestaurar && barraInferior) {
            barraInferior.removeChild(botonRestaurar);
        }
        ventana.style.zIndex = ++zIndexActual;
    }
}

function maximizarVentana(id) {
    const ventana = document.getElementById('ventana-' + id);
    const escritorio = document.getElementById('escritorio');
    if (!ventana || !escritorio) return;

    if (!estadoVentanas[id]) {
        estadoVentanas[id] = { maximizada: false, minimizada: false, original: {
            width: ventana.style.width,
            height: ventana.style.height,
            top: ventana.style.top,
            left: ventana.style.left,
            resize: ventana.style.resize
        }};
    }

    if (!estadoVentanas[id].maximizada) {
        // Guardar valores originales
        estadoVentanas[id].original.width = ventana.style.width;
        estadoVentanas[id].original.height = ventana.style.height;
        estadoVentanas[id].original.top = ventana.style.top;
        estadoVentanas[id].original.left = ventana.style.left;
        estadoVentanas[id].original.resize = ventana.style.resize;

        // Maximizar
        ventana.style.top = '0';
        ventana.style.left = '0';
        ventana.style.width = escritorio.clientWidth + 'px';
        ventana.style.height = (escritorio.clientHeight - 40) + 'px';
        ventana.style.resize = 'none';
        estadoVentanas[id].maximizada = true;
    } else {
        // Restaurar valores originales
        ventana.style.top = estadoVentanas[id].original.top;
        ventana.style.left = estadoVentanas[id].original.left;
        ventana.style.width = estadoVentanas[id].original.width;
        ventana.style.height = estadoVentanas[id].original.height;
        ventana.style.resize = estadoVentanas[id].original.resize;
        estadoVentanas[id].maximizada = false;
    }
}

// Escuchar mensajes postMessage desde ventanas hijas o contenido inyectado
window.addEventListener('message', function (e) {
    if (!e.data) return;
    // Aceptamos mensajes desde el mismo origen o desde '*'
    const accion = e.data.accion;
    if (accion !== 'cliente_creado') return;

    console.log('ventanas.js: message recibido accion=cliente_creado', e.data);

    // 1) Cerrar ventana de nuevo cliente si existe
    const vNuevo = document.getElementById('ventana-nuevo-cliente');
    if (vNuevo) vNuevo.remove();

    // 2) Refrescar contenido de la ventana clientes (si está abierta)
    const vClientes = document.getElementById('ventana-clientes');
    if (!vClientes) {
        console.log('ventanas.js: ventana-clientes no abierta, nada que refrescar');
        return;
    }

    // Buscamos el contenedor de contenido dentro de la ventana clientes
    const cont = document.getElementById('contenido-ventana-clientes') || vClientes.querySelector('.contenido-clientes') || vClientes.querySelector('#contenido-ventana-clientes');
    if (!cont) {
        console.log('ventanas.js: contenedor de clientes no encontrado');
        return;
    }

    // Recargar parcial via fetch y actualizar
    fetch('/ordenes/clientes/parcial/')
        .then(res => res.text())
        .then(html => {
            cont.innerHTML = html;
            if (typeof window.clientesInit === 'function') {
                try {
                    window.clientesInit(cont);
                } catch (err) {
                    console.error('ventanas.js: error al ejecutar clientesInit', err);
                }
            } else {
                // fallback: emitir evento para que alguien más inicialice
                document.dispatchEvent(new CustomEvent('clientes:rendered', { detail: { container: cont, id: 'clientes' } }));
            }
            console.log('ventanas.js: Lista de clientes refrescada tras crear nuevo.');
        })
        .catch(err => console.error('ventanas.js: Error al refrescar lista de clientes:', err));
});