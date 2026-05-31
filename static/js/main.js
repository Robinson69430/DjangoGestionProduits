/* ── GestStock — main.js ─────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  initAlerts();
  initModals();
  initSidebarActive();
  initStockBars();
  initColorInputs();
});

/* ── Alerts auto-dismiss ─────────────────────────────────── */
function initAlerts() {
  document.querySelectorAll('.alert').forEach(alert => {
    // Bouton fermer
    const btn = alert.querySelector('.alert-close');
    if (btn) btn.addEventListener('click', () => dismissAlert(alert));

    // Auto-dismiss après 5s pour success/info
    if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
      setTimeout(() => dismissAlert(alert), 5000);
    }
  });
}

function dismissAlert(el) {
  el.style.transition = 'opacity 0.3s ease, transform 0.3s ease, max-height 0.3s ease, margin 0.3s ease, padding 0.3s ease';
  el.style.opacity = '0';
  el.style.transform = 'translateY(-4px)';
  el.style.maxHeight = el.offsetHeight + 'px';
  requestAnimationFrame(() => {
    el.style.maxHeight = '0';
    el.style.marginBottom = '0';
    el.style.paddingTop = '0';
    el.style.paddingBottom = '0';
  });
  setTimeout(() => el.remove(), 350);
}

/* ── Modals ──────────────────────────────────────────────── */
function initModals() {
  // Ouvrir
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.modalOpen;
      const modal = document.getElementById(id);
      if (modal) modal.classList.add('open');
    });
  });

  // Fermer (backdrop ou bouton close)
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', e => {
      if (e.target === backdrop) backdrop.classList.remove('open');
    });
    backdrop.querySelectorAll('[data-modal-close]').forEach(btn => {
      btn.addEventListener('click', () => backdrop.classList.remove('open'));
    });
  });

  // Fermer avec Échap
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-backdrop.open').forEach(m => m.classList.remove('open'));
    }
  });
}

/* ── Sidebar lien actif ──────────────────────────────────── */
function initSidebarActive() {
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    if (path === href || (href !== '/' && path.startsWith(href))) {
      link.classList.add('active');
    }
  });
}

/* ── Barres de stock ─────────────────────────────────────── */
function initStockBars() {
  document.querySelectorAll('.stock-bar-fill[data-pct]').forEach(bar => {
    const pct = Math.min(100, Math.max(0, parseFloat(bar.dataset.pct)));
    bar.style.width = pct + '%';

    if (pct <= 20) {
      bar.style.background = 'var(--danger)';
    } else if (pct <= 50) {
      bar.style.background = 'var(--warning)';
    } else {
      bar.style.background = 'var(--accent)';
    }
  });
}

/* ── Aperçu couleur catégorie ────────────────────────────── */
function initColorInputs() {
  document.querySelectorAll('input[type="color"][data-preview]').forEach(input => {
    const previewId = input.dataset.preview;
    const preview = document.getElementById(previewId);
    if (!preview) return;
    const update = () => { preview.style.background = input.value; };
    input.addEventListener('input', update);
    update();
  });
}

/* ── Confirm delete ──────────────────────────────────────── */
function confirmDelete(formId, name) {
  const modal = document.getElementById('modal-confirm-delete');
  if (!modal) return;

  const label = modal.querySelector('[data-delete-name]');
  if (label) label.textContent = name;

  const form = document.getElementById(formId);
  const confirmBtn = modal.querySelector('[data-confirm-submit]');
  if (confirmBtn && form) {
    confirmBtn.onclick = () => form.submit();
  }

  modal.classList.add('open');
}

/* ── Toggle mouvement type ───────────────────────────────── */
function setMovementType(type) {
  const input = document.getElementById('movement-type');
  if (input) input.value = type;

  document.querySelectorAll('[data-mov-type]').forEach(btn => {
    btn.classList.toggle('btn-primary', btn.dataset.movType === type);
    btn.classList.toggle('btn-outline', btn.dataset.movType !== type);
  });
}