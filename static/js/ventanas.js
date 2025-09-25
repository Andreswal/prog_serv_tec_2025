let estadoVentanas = {};
let zIndexActual = 1000; // z-index base para ventanas

function abrirVentana(id, url) {
  if (document.getElementById('ventana-' + id)) {
    document.getElementById('ventana-' + id).style.zIndex = ++zIndexActual;
    return;
  }

  const ventana = document.createElement('div');
  ventana.id = 'ventana-' + id;
  ventana.className = 'ventana-flotante';
  ventana.style.position = 'fixed'; // ← corregido: antes era 'absolute'
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

  ventana.innerHTML = `
    <div class="barra-ventana" style="background: #222; color: white; padding: 5px; cursor: move;">
      <span>${id.toUpperCase()}</span>
      <div style="float: right;">
        <button onclick="alternarMinimizar('${id}')" style="margin-right: 5px;">🗕</button>
        <button onclick="maximizarVentana('${id}')" style="margin-right: 5px;">🗖</button>
        <button onclick="document.getElementById('ventana-${id}').remove()">❌</button>
      </div>
    </div>
    <div class="contenido-${id}" style="padding: 10px;">Cargando...</div>
  `;

  document.getElementById('escritorio').appendChild(ventana);

  fetch(url)
    .then(res => res.text())
    .then(html => {
      const cont = ventana.querySelector('.contenido-' + id);
      if (cont) cont.innerHTML = html;
    })
    .catch(() => {
      const cont = ventana.querySelector('.contenido-' + id);
      if (cont) cont.innerHTML = "<div class='text-danger'>Error al cargar contenido.</div>";
    });

  hacerMovible(ventana);

  ventana.addEventListener('mousedown', () => {
    ventana.style.zIndex = ++zIndexActual;
  });

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
