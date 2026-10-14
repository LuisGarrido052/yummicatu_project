/**
 * Yummi Catu - Interacciones JavaScript
 * Soporte para menú móvil responsive, interactividad de tarjetas y validaciones amigables.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Menú hamburguesa responsive en móviles
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navMenu.classList.toggle('open');
      const isExpanded = navMenu.classList.contains('open');
      navToggle.setAttribute('aria-expanded', isExpanded);
    });
  }

  // 2. Cierre automático de mensajes de alerta tras 6 segundos
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 500);
    }, 6000);
  });

  // 3. Formateador dinámico para el campo RUN chileno en el formulario
  const runInput = document.getElementById('id_run');
  if (runInput) {
    runInput.addEventListener('input', (e) => {
      let valor = e.target.value.replace(/[^0-9kK]/g, '').toUpperCase();
      if (valor.length > 9) {
        valor = valor.slice(0, 9);
      }
      if (valor.length > 1) {
        const cuerpo = valor.slice(0, -1);
        const dv = valor.slice(-1);
        e.target.value = `${cuerpo}-${dv}`;
      } else {
        e.target.value = valor;
      }
    });
  }

  // 4. Preselección de producto en el formulario si viene por URL (ej: /formulario/?producto=1)
  const urlParams = new URLSearchParams(window.location.search);
  const selectedProdId = urlParams.get('producto');
  const selectElement = document.getElementById('id_producto');
  if (selectedProdId && selectElement) {
    selectElement.value = selectedProdId;
  }
});
