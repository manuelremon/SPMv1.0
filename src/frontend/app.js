// Calcula la URL base del backend. Preferimos hablar con el mismo origen

// para evitar problemas de CSP/CORS cuando se sirve tras Nginx.

const API = (function () {

  if (location.protocol === "file:") {

    return "http://127.0.0.1:5001/api";

  }

  return `${location.origin}/api`;

})();

const $ = (sel) => document.querySelector(sel);

const on = (el, ev, fn) => el && el.addEventListener(ev, fn);


const THEME_STORAGE_KEY = "spm-theme";
const VALID_THEMES = new Set(["light", "dark"]);
const prefersLightQuery = window.matchMedia ? window.matchMedia("(prefers-color-scheme: light)") : null;

function readStoredTheme() {
  try {
    return localStorage.getItem(THEME_STORAGE_KEY);
  } catch (_error) {
    return null;
  }
}

function storeThemePreference(theme) {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch (_error) {
    /* Ignorado: almacenamiento no disponible */
  }
}

function resolvePreferredTheme() {
  const stored = readStoredTheme();
  if (stored && VALID_THEMES.has(stored)) {
    return stored;
  }
  if (prefersLightQuery && typeof prefersLightQuery.matches === "boolean") {
    return prefersLightQuery.matches ? "light" : "dark";
  }
  return "dark";
}

function updateThemeToggleUi(theme) {
  const toggle = document.getElementById("themeToggle");
  if (!toggle) {
    return;
  }
  const isLight = theme === "light";
  toggle.setAttribute("aria-pressed", String(isLight));
  toggle.setAttribute("aria-label", isLight ? "Cambiar a tema oscuro" : "Cambiar a tema claro");
  toggle.dataset.theme = theme;

  const icon = toggle.querySelector(".theme-toggle__icon");
  if (icon) {
    icon.textContent = isLight ? "☀️" : "🌙";
  }

  const text = toggle.querySelector(".theme-toggle__text");
  if (text) {
    text.textContent = isLight ? "Tema claro" : "Tema oscuro";
  }
}

function applyTheme(theme, { persist = true } = {}) {
  const selected = VALID_THEMES.has(theme) ? theme : "dark";
  document.body.dataset.theme = selected;
  document.documentElement.style.colorScheme = selected;
  updateThemeToggleUi(selected);
  if (persist) {
    storeThemePreference(selected);
  }
}

function initThemeToggle() {
  const toggle = document.getElementById("themeToggle");
  if (!toggle) {
    return;
  }

  let currentTheme = VALID_THEMES.has(document.body.dataset.theme)
    ? document.body.dataset.theme
    : resolvePreferredTheme();

  if (!VALID_THEMES.has(document.body.dataset.theme)) {
    applyTheme(currentTheme, { persist: false });
  } else {
    updateThemeToggleUi(currentTheme);
  }

  toggle.addEventListener("click", () => {
    currentTheme = currentTheme === "dark" ? "light" : "dark";
    applyTheme(currentTheme);
  });

  if (prefersLightQuery) {
    const systemThemeListener = (event) => {
      const stored = readStoredTheme();
      if (stored && VALID_THEMES.has(stored)) {
        return;
      }
      currentTheme = event.matches ? "light" : "dark";
      applyTheme(currentTheme, { persist: false });
    };

    if (typeof prefersLightQuery.addEventListener === "function") {
      prefersLightQuery.addEventListener("change", systemThemeListener);
    } else if (typeof prefersLightQuery.addListener === "function") {
      prefersLightQuery.addListener(systemThemeListener);
    }
  }
}

applyTheme(resolvePreferredTheme(), { persist: false });



function ensureToastsContainer() {

  let container = document.getElementById("toasts");

  if (!container) {

    container = document.createElement("div");

    container.id = "toasts";

    container.className = "toasts";

    document.body.appendChild(container);

  }

  return container;

}



function toast(msg, ok = false) {

  if (ok && typeof state !== "undefined" && state.preferences && state.preferences.realtimeToasts === false) {

    return;

  }

  const container = ensureToastsContainer();

  const node = document.createElement("div");

  node.className = `toast ${ok ? "ok" : "err"}`;

  node.setAttribute("role", "status");

  node.textContent = msg;

  node.classList.add("enter");

  container.appendChild(node);

  requestAnimationFrame(() => {

    node.classList.add("enter-active");

  });

  setTimeout(() => {

    node.classList.add("fade-out");

    node.addEventListener("transitionend", () => node.remove(), { once: true });

  }, 3400);

}



async function api(path, opts = {}) {

  const config = {

    credentials: "include",

    headers: { "Content-Type": "application/json" },

    ...opts,

  };

  const res = await fetch(`${API}${path}`, config);

  if (!res.ok) {

    let err = "Error de red";

    try {

      const json = await res.json();

      err = json.error?.message || err;

    } catch (_ignored) {}

    throw new Error(err);

  }

  const isJson = res.headers

    .get("content-type")

    ?.includes("application/json");

  return isJson ? res.json() : res.text();

}



const show = (el) => el.classList.remove("hide");

const hide = (el) => el.classList.add("hide");



function isNotFoundError(err) {

  const msg = (err?.message || "").toLowerCase();

  return msg.includes("no encontrada") || msg.includes("no existe") || msg.includes("notfound");

}



const currencyFormatter = new Intl.NumberFormat("es-AR", {

  style: "currency",

  currency: "USD",

  minimumFractionDigits: 2,

});



const formatCurrency = (value) => currencyFormatter.format(Number(value || 0));



function escapeHtml(value) {

  return String(value || "")

    .replace(/&/g, "&amp;")

    .replace(/</g, "&lt;")

    .replace(/>/g, "&gt;")

    .replace(/"/g, "&quot;")

    .replace(/'/g, "&#39;");

}



function formatDateTime(value) {

  if (!value) return "â€”";

  const normalised = typeof value === "string" ? value.replace("T", " ") : value;

  const date = new Date(normalised);

  if (Number.isNaN(date.getTime())) {

    return typeof value === "string" ? value : "â€”";

  }

  return date.toLocaleString();

}



function formatDateOnly(value) {

  if (!value) return "â€”";

  const normalised = typeof value === "string" ? value.replace("T", " ") : value;

  const date = new Date(normalised);

  if (Number.isNaN(date.getTime())) {

    return typeof value === "string" ? value : "â€”";

  }

  return date.toLocaleDateString();

}



function formatPercentage(value) {

  const numeric = Number(value);

  if (!Number.isFinite(numeric) || numeric <= 0) {

    return "0%";

  }

  if (numeric >= 100) {

    return "100%";

  }

  const digits = numeric >= 10 ? 0 : 1;

  return `${numeric.toFixed(digits)}%`;

}



const ICONS = {

  pencil: `

    <svg aria-hidden="true" viewBox="0 0 24 24" focusable="false">

      <path d="M3 17.25V21h3.75l11-11-3.75-3.75-11 11ZM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83Z"></path>

    </svg>

  `,

  plus: `

    <svg aria-hidden="true" viewBox="0 0 24 24" focusable="false">

      <path d="M13 11V5a1 1 0 0 0-2 0v6H5a1 1 0 0 0 0 2h6v6a1 1 0 0 0 2 0v-6h6a1 1 0 0 0 0-2Z"></path>

    </svg>

  `,

};



const centersRequestState = {

  modal: null,

  selected: new Set(),

  options: [],

  existing: new Set(),

  keyListenerBound: false,

};



const ANIMATED_SELECTORS = [

  ".pane",

  ".card",

  ".metric-card",

  ".notification-item",

  ".detail-section",

  ".content-section > *:not(.page-header)",

  ".admin-material-detail",

  ".admin-user-detail",

  ".archivos-adjuntos",

];

const REDUCED_MOTION_MEDIA = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;

const dynamicFilterHandlers = new WeakMap();

let animationObserver = null;

let effectsEnabled = true;

let headerNavInitialized = false;



function markAnimatedElements(scope = document) {

  if (!scope || (scope === document && !document.body)) {

    return [];

  }

  const nodes = new Set();

  ANIMATED_SELECTORS.forEach((selector) => {

    scope.querySelectorAll(selector).forEach((element) => {

      if (!element.dataset.animate) {

        element.dataset.animate = "fade-up";

      }

      nodes.add(element);

    });

  });

  scope.querySelectorAll("[data-animate]").forEach((element) => nodes.add(element));

  return Array.from(nodes);

}



function teardownAnimations() {

  if (animationObserver) {

    animationObserver.disconnect();

    animationObserver = null;

  }

}



function refreshAnimations(scope = document) {

  const elements = markAnimatedElements(scope);

  if (!elements.length) {

    return;

  }

  if (!effectsEnabled) {

    elements.forEach((el) => el.classList.add("is-visible"));

    teardownAnimations();

    return;

  }

  if (REDUCED_MOTION_MEDIA && REDUCED_MOTION_MEDIA.matches) {

    elements.forEach((el) => el.classList.add("is-visible"));

    teardownAnimations();

    return;

  }

  if (!animationObserver) {

    animationObserver = new IntersectionObserver(

      (entries) => {

        entries.forEach((entry) => {

          if (entry.isIntersecting) {

            entry.target.classList.add("is-visible");

            animationObserver.unobserve(entry.target);

          }

        });

      },

      { threshold: 0.12, rootMargin: "0px 0px -10%" },

    );

  }

  elements.forEach((el) => {

    if (animationObserver) {

      animationObserver.observe(el);

    }

  });

}



function applyEffectsPreference(enabled) {

  effectsEnabled = enabled;

  document.documentElement.dataset.effects = enabled ? "on" : "off";

  if (document.body) {

    document.body.dataset.effects = enabled ? "on" : "off";

  }

  if (enabled) {

    document.documentElement.style.removeProperty("--current-motion-scale");

    refreshAnimations();

  } else {

    teardownAnimations();

    document.querySelectorAll("[data-animate]").forEach((el) => {

      el.classList.add("is-visible");

    });

  }

}



const skeletonRegistry = new WeakMap();



function showTableSkeleton(target, { rows = 6, columns = null } = {}) {

  const table = typeof target === "string" ? document.querySelector(target) : target;

  if (!table) {

    return () => {};

  }

  const tbody = table.tBodies?.[0] || table.querySelector("tbody");

  if (!tbody) {

    return () => {};

  }

  const colCount = columns || table.tHead?.rows?.[0]?.cells?.length || 4;

  const skeletonRows = [];

  for (let rowIndex = 0; rowIndex < rows; rowIndex += 1) {

    const tr = document.createElement("tr");

    tr.className = "skeleton-row";

    for (let colIndex = 0; colIndex < colCount; colIndex += 1) {

      const td = document.createElement("td");

      const span = document.createElement("span");

      span.className = "skeleton skeleton-line";

      td.appendChild(span);

      tr.appendChild(td);

    }

    tbody.appendChild(tr);

    skeletonRows.push(tr);

  }

  skeletonRegistry.set(table, skeletonRows);

  return () => {

    (skeletonRegistry.get(table) || []).forEach((row) => row.remove());

    skeletonRegistry.delete(table);

  };

}



function setButtonLoading(button, isLoading) {

  if (!button) {

    return;

  }

  if (isLoading) {

    button.dataset.loading = "true";

    button.classList.add("is-loading");

    button.setAttribute("aria-busy", "true");

  } else {

    button.dataset.loading = "false";

    button.classList.remove("is-loading");

    button.removeAttribute("aria-busy");

  }

}



function initDynamicFilters(scope = document) {

  scope.querySelectorAll('[data-filter-target]').forEach((input) => {

    if (dynamicFilterHandlers.has(input)) {

      return;

    }

    const targetSelector = input.dataset.filterTarget;

    const itemsSelector = input.dataset.filterItems || "tr";

    const emptySelector = input.dataset.filterEmpty || "";

    const target = document.querySelector(targetSelector);

    if (!target) {

      return;

    }

    const handler = () => {

      const value = (input.value || "").trim().toLowerCase();

      const items = target.querySelectorAll(itemsSelector);

      let visibleCount = 0;

      items.forEach((item) => {

        const matches = !value || (item.textContent || "").toLowerCase().includes(value);

        item.style.display = matches ? "" : "none";

        if (matches) {

          visibleCount += 1;

        }

      });

      if (emptySelector) {

        const emptyNode = document.querySelector(emptySelector);

        if (emptyNode) {

          emptyNode.style.display = visibleCount === 0 ? "block" : "none";

        }

      }

    };

    input.addEventListener("input", handler);

    dynamicFilterHandlers.set(input, handler);

    handler();

  });

}



function setSubmenuTabState(submenu, enabled) {

  if (!submenu) {

    return;

  }

  const focusable = submenu.querySelectorAll("a,button");

  focusable.forEach((node) => {

    if (enabled) {

      node.removeAttribute("tabindex");

    } else {

      node.setAttribute("tabindex", "-1");

    }

  });

}



function closeSubmenu(item) {

  if (!item) {

    return;

  }

  const trigger = item.querySelector(":scope > .app-menu__trigger");

  const submenu = item.querySelector(":scope > .app-submenu");

  item.classList.remove("is-open");

  if (trigger) {

    trigger.setAttribute("aria-expanded", "false");

  }

  if (submenu) {

    submenu.hidden = true;

    submenu.setAttribute("aria-hidden", "true");

    setSubmenuTabState(submenu, false);

    submenu.querySelectorAll(".has-submenu").forEach((child) => {

      if (child !== item) {

        closeSubmenu(child);

      }

    });

  }

}



function openSubmenu(item) {

  if (!item) {

    return;

  }

  const trigger = item.querySelector(":scope > .app-menu__trigger");

  const submenu = item.querySelector(":scope > .app-submenu");

  item.classList.add("is-open");

  if (trigger) {

    trigger.setAttribute("aria-expanded", "true");

  }

  if (submenu) {

    submenu.hidden = false;

    submenu.removeAttribute("hidden");

    submenu.setAttribute("aria-hidden", "false");

    setSubmenuTabState(submenu, true);

  }

}



function closeAllSubmenus(except = null, scope = document) {

  scope.querySelectorAll(".has-submenu").forEach((item) => {

    if (item === except) {

      return;

    }

    closeSubmenu(item);

  });

}



function initializeHeaderSubmenus(root = document) {

  root.querySelectorAll(".has-submenu").forEach((item) => {

    closeSubmenu(item);

  });

}



function setupHeaderNav() {

  const nav = document.getElementById("primaryNav");

  if (!nav) return;



  initializeHeaderSubmenus(nav);



  nav.addEventListener("click", (event) => {

    const trigger = event.target instanceof Element ? event.target.closest(".app-menu__trigger") : null;

    if (trigger && nav.contains(trigger)) {

      event.preventDefault();

      const item = trigger.closest(".has-submenu");

      if (!item) return;

      const isOpen = item.classList.contains("is-open");

      closeAllSubmenus(item, nav);

      if (isOpen) {

        closeSubmenu(item);

      } else {

        openSubmenu(item);

      }

      return;

    }

    const link = event.target instanceof Element ? event.target.closest(".app-menu__link") : null;

    if (link && nav.contains(link)) {

      closeAllSubmenus(null, nav);

    }

  });



  nav.addEventListener("keydown", (event) => {

    const trigger = event.target instanceof Element ? event.target.closest(".app-menu__trigger") : null;

    if (!trigger || !nav.contains(trigger)) {

      return;

    }

    const item = trigger.closest(".has-submenu");

    if (!item) {

      return;

    }

    if (event.key === "Escape") {

      event.preventDefault();

      closeSubmenu(item);

      trigger.focus({ preventScroll: true });

      return;

    }

    if (event.key === "ArrowDown") {

      event.preventDefault();

      if (!item.classList.contains("is-open")) {

        closeAllSubmenus(item, nav);

        openSubmenu(item);

      }

      const submenu = item.querySelector(":scope > .app-submenu");

      if (submenu) {

        const firstFocusable = submenu.querySelector("a,button");

        firstFocusable?.focus({ preventScroll: true });

      }

    }

  });



  nav.addEventListener("focusout", (event) => {

    if (!nav.contains(event.relatedTarget)) {

      closeAllSubmenus(null, nav);

    }

  });



  document.addEventListener("click", (event) => {

    if (!nav.contains(event.target)) {

      closeAllSubmenus(null, nav);

    }

  });

}



function finalizePage(scope = document) {

  document.body?.classList.add("is-ready");

  markAnimatedElements(scope);

  refreshAnimations(scope);

  initDynamicFilters(scope);

  setupHeaderNav();

  configureRequestsMenu();

}



const tableSortStates = new WeakMap();



function refreshSortableTables(root = document) {

  const scope = root instanceof Element ? root : document;

  scope.querySelectorAll("table[data-sortable-table]").forEach((table) => {

    ensureTableSortable(table);

  });

}



function ensureTableSortable(target) {

  const table = typeof target === "string" ? document.querySelector(target) : target;

  if (!table) {

    return;

  }

  let state = tableSortStates.get(table);

  if (!state) {

    state = { column: null, direction: 1 };

    tableSortStates.set(table, state);

    initTableSortable(table, state);

  }

  updateSortIndicators(table, state);

  if (typeof state.column === "number") {

    sortTableRows(table, state.column, state.direction, { preserveState: true });

  }

}



function initTableSortable(table, state) {

  if (!table || table.dataset.sortableInit === "1") {

    return;

  }

  const thead = table.querySelector("thead");

  if (!thead) {

    return;

  }

  table.dataset.sortableInit = "1";

  const headers = Array.from(thead.querySelectorAll("th"));

  headers.forEach((th, index) => {

    const rawLabel = (th.textContent || "").trim() || `Columna ${index + 1}`;

    const safeLabel = escapeHtml(rawLabel);

    const button = document.createElement("button");

    button.type = "button";

    button.className = "sort-button";

    button.dataset.label = rawLabel;

    button.innerHTML = `<span class="sort-label">${safeLabel}</span><span class="sort-icon">A-Z</span>`;

    button.addEventListener("click", () => {

      let nextDirection = 1;

      if (state.column === index) {

        nextDirection = state.direction === 1 ? -1 : 1;

      }

      state.column = index;

      state.direction = nextDirection;

      sortTableRows(table, index, nextDirection);

      updateSortIndicators(table, state);

    });

    th.classList.add("sortable");

    th.setAttribute("data-sort", "none");

    th.replaceChildren(button);

  });

}



function sortTableRows(table, columnIndex, direction, options = {}) {

  if (!table || !table.tBodies || !table.tBodies.length) {

    return;

  }

  const tbody = table.tBodies[0];

  const rows = Array.from(tbody.querySelectorAll("tr"));

  if (!rows.length) {

    return;

  }

  const multiplier = direction === -1 ? -1 : 1;

  rows.sort((rowA, rowB) => {

    const aToken = getCellSortToken(rowA, columnIndex);

    const bToken = getCellSortToken(rowB, columnIndex);

    if (aToken.type === bToken.type) {

      if (aToken.type === "number" || aToken.type === "date") {

        return (aToken.value - bToken.value) * multiplier;

      }

      return aToken.value.localeCompare(bToken.value, "es", {

        sensitivity: "base",

        numeric: true,

      }) * multiplier;

    }

    return aToken.raw.localeCompare(bToken.raw, "es", {

      sensitivity: "base",

      numeric: true,

    }) * multiplier;

  });

  rows.forEach((row) => tbody.appendChild(row));

  if (!options.preserveState) {

    const state = tableSortStates.get(table);

    if (state) {

      state.column = columnIndex;

      state.direction = multiplier;

    }

  }



  refreshSortableTables();

}



function getCellSortToken(row, columnIndex) {

  const cell = row.cells?.[columnIndex];

  if (!cell) {

    return { type: "string", value: "", raw: "" };

  }

  const dataValue = cell.getAttribute("data-sort");

  const raw = (dataValue ?? cell.textContent ?? "").trim();

  const numeric = parseNumericValue(raw);

  if (numeric !== null) {

    return { type: "number", value: numeric, raw };

  }

  const parsedDate = Date.parse(raw);

  if (!Number.isNaN(parsedDate)) {

    return { type: "date", value: parsedDate, raw };

  }

  return { type: "string", value: raw.toLowerCase(), raw };

}



function parseNumericValue(raw) {

  if (!raw) {

    return null;

  }

  const normalized = raw

    .replace(/\s+/g, "")

    .replace(/[^0-9,.-]/g, "");

  if (!normalized) {

    return null;

  }

  let candidate = normalized;

  if (candidate.includes(",") && (!candidate.includes(".") || candidate.lastIndexOf(",") > candidate.lastIndexOf("."))) {

    candidate = candidate.replace(/\./g, "").replace(",", ".");

  } else {

    candidate = candidate.replace(/,/g, "");

  }

  if (!candidate || candidate === "-" || candidate === ".") {

    return null;

  }

  const numeric = Number(candidate);

  return Number.isFinite(numeric) ? numeric : null;

}



function updateSortIndicators(table, state) {

  if (!table) {

    return;

  }

  const thead = table.querySelector("thead");

  if (!thead) {

    return;

  }

  const headers = thead.querySelectorAll("th.sortable");

  headers.forEach((th, index) => {

    const button = th.querySelector("button.sort-button");

    const icon = button?.querySelector(".sort-icon");

    const baseLabel = button?.dataset.label || (th.textContent || "").trim() || `Columna ${index + 1}`;

    const isActive = state && state.column === index;

    if (icon) {

      if (isActive) {

        icon.textContent = state.direction === -1 ? "Z-A" : "A-Z";

        th.setAttribute("data-sort", state.direction === -1 ? "desc" : "asc");

      } else {

        icon.textContent = "A-Z";

        th.setAttribute("data-sort", "none");

      }

    }

    if (button) {

      const dirLabel = isActive ? (state.direction === -1 ? "Z-A" : "A-Z") : "A-Z";

      button.setAttribute("aria-label", `Ordenar por ${baseLabel}${isActive ? ` (${dirLabel})` : ""}`);

    }

  });

}



function trimChatHistory() {

  const max = CHAT_HISTORY_LIMIT * 2;

  if (state.chat.messages.length > max) {

    state.chat.messages = state.chat.messages.slice(-max);

  }

}



function renderChatMessages() {

  const container = document.getElementById("chatbotMessages");

  if (!container) {

    return;

  }

  container.innerHTML = "";

  if (!state.chat.messages.length) {

    const empty = document.createElement("div");

    empty.className = "chatbot-empty";

    empty.textContent = "Todavia no iniciaste una conversacion. Escribi tu consulta.";

    container.appendChild(empty);

    return;

  }

  const fragment = document.createDocumentFragment();

  state.chat.messages.forEach((msg) => {

    const wrapper = document.createElement("div");

    const role = msg.role === "assistant" ? "assistant" : "user";

    wrapper.className = `chatbot-message chatbot-message--${role}`;

    wrapper.innerHTML = `<p>${escapeHtml(msg.content)}</p>`;

    fragment.appendChild(wrapper);

  });

  container.appendChild(fragment);

  container.scrollTop = container.scrollHeight;

}



function updateChatbotControls() {

  const input = document.getElementById("chatbotInput");

  const sendBtn = document.getElementById("chatbotSend");

  const status = document.getElementById("chatbotStatus");

  if (input) {

    input.disabled = state.chat.isSending;

  }

  if (sendBtn) {

    sendBtn.disabled = state.chat.isSending;

    sendBtn.textContent = state.chat.isSending ? "Enviando..." : "Enviar";

  }

  if (status) {

    status.textContent = state.chat.isSending ? "Consultando modelo..." : "";

  }

}



function toggleChatbotPanel(forceState) {

  const panel = document.getElementById("chatbotPanel");

  const fab = document.getElementById("chatbotFab");

  if (!panel || !fab) {

    return;

  }

  const nextState = typeof forceState === "boolean" ? forceState : !state.chat.isOpen;

  state.chat.isOpen = nextState;

  panel.classList.toggle("chatbot-panel--open", nextState);

  panel.setAttribute("aria-hidden", nextState ? "false" : "true");

  fab.classList.toggle("chatbot-fab--hidden", nextState);

  if (nextState) {

    renderChatMessages();

    const input = document.getElementById("chatbotInput");

    if (input) {

      input.focus();

    }

  }

}



async function processChatbotPrompt(rawText) {

  const text = String(rawText || "").trim();

  if (!text || state.chat.isSending) {

    return;

  }

  const historyPayload = state.chat.messages.slice(-(CHAT_HISTORY_LIMIT - 1)).map((msg) => ({

    role: msg.role,

    content: msg.content,

  }));

  const userMessage = { role: "user", content: text };

  state.chat.messages.push(userMessage);

  trimChatHistory();

  renderChatMessages();



  state.chat.isSending = true;

  updateChatbotControls();



  try {

    const resp = await api("/chatbot", {

      method: "POST",

      body: JSON.stringify({ message: text, history: historyPayload }),

    });

    if (!resp?.ok) {

      throw new Error(resp?.error?.message || "No se obtuvo respuesta");

    }

    const reply = String(resp.message?.content || "No recibimos respuesta del asistente.").trim();

    state.chat.messages.push({ role: "assistant", content: reply });

  } catch (err) {

    const detail = err?.message || "No se pudo contactar al asistente";

    state.chat.messages.push({ role: "assistant", content: `Hubo un problema: ${detail}` });

    toast(detail);

  } finally {

    trimChatHistory();

    state.chat.isSending = false;

    renderChatMessages();

    updateChatbotControls();

  }

}



function ensureChatbotWidget() {

  if (document.getElementById("chatbotFab")) {

    return;

  }

  const fab = document.createElement("button");

  fab.id = "chatbotFab";

  fab.type = "button";

  fab.className = "chatbot-fab";

  fab.innerHTML = `

    <img src="assets/chatbot-icon.svg" alt="Abrir asistente" class="chatbot-fab__icon" aria-hidden="true"/>

    <span class="sr-only">Chat con asistente</span>

  `;

  document.body.appendChild(fab);



  const panel = document.createElement("section");

  panel.id = "chatbotPanel";

  panel.className = "chatbot-panel";

  panel.setAttribute("aria-hidden", "true");

  panel.innerHTML = `

    <header class="chatbot-panel__header">

      <span class="chatbot-panel__title">Asistente SPM</span>

      <button type="button" class="chatbot-panel__close" id="chatbotClose" aria-label="Cerrar asistente">X</button>

    </header>

    <div class="chatbot-panel__messages" id="chatbotMessages"></div>

    <p class="chatbot-panel__status" id="chatbotStatus"></p>

    <form class="chatbot-panel__form" id="chatbotForm">

      <label for="chatbotInput" class="sr-only">Mensaje para el asistente</label>

      <textarea id="chatbotInput" rows="3" placeholder="Escribi tu consulta..." required></textarea>

      <div class="chatbot-panel__actions">

        <button type="submit" id="chatbotSend" class="btn">Enviar</button>

      </div>

    </form>

  `;

  document.body.appendChild(panel);



  fab.addEventListener("click", () => {

    toggleChatbotPanel(true);

  });



  const closeBtn = document.getElementById("chatbotClose");

  if (closeBtn) {

    closeBtn.addEventListener("click", (ev) => {

      ev.preventDefault();

      toggleChatbotPanel(false);

    });

  }



  const form = document.getElementById("chatbotForm");

  const input = document.getElementById("chatbotInput");

  if (form) {

    form.addEventListener("submit", async (ev) => {

      ev.preventDefault();

      if (!input) {

        return;

      }

      const value = input.value;

      if (!value.trim() || state.chat.isSending) {

        return;

      }

      input.value = "";

      await processChatbotPrompt(value);

    });

  }

  if (input) {

    input.addEventListener("keydown", (ev) => {

      if (ev.key === "Enter" && (ev.ctrlKey || ev.metaKey)) {

        ev.preventDefault();

        form?.dispatchEvent(new Event("submit", { cancelable: true }));

      }

    });

  }



  document.addEventListener("keydown", (ev) => {

    if (ev.key === "Escape" && state.chat.isOpen) {

      toggleChatbotPanel(false);

    }

  });
}



function initChatbotWidget() {

  ensureChatbotWidget();

  if (!state.chat.messages.length) {

    state.chat.messages.push({

      role: "assistant",

      content: "Hola, soy el asistente de SPM. En que puedo ayudarte hoy?",

    });

  }

  renderChatMessages();

  updateChatbotControls();

}



function initHomeHero(userName) {

  const node = document.getElementById("homeTypewriter");

  if (!node || node.dataset.typewriterDone === "1") {

    return;

  }

  const template = node.dataset.typewriter || node.textContent || "";

  const message = template.replace(/\{\{\s*name\s*\}\}/gi, userName || "").replace(/\s{2,}/g, " ").trim();

  if (!message) {

    node.classList.add("is-finished");

    node.dataset.typewriterDone = "1";

    return;

  }

  node.textContent = "";

  node.dataset.typewriterDone = "1";

  node.classList.add("is-typing");

  let index = 0;

  const delay = Number(node.dataset.typewriterSpeed) || 48;

  const initialDelay = Number(node.dataset.typewriterDelay) || 260;



  const tick = () => {

    index += 1;

    node.textContent = message.slice(0, index);

    if (index < message.length) {

      window.setTimeout(tick, delay);

    } else {

      node.classList.remove("is-typing");

      node.classList.add("is-finished");

    }

  };



  window.setTimeout(tick, initialDelay);

}



const STATUS_LABELS = {

  draft: "Borrador",

  finalizada: "Finalizada",

  cancelada: "Cancelada",

  pendiente_de_aprobacion: "Pendiente de aprobaciÃ³n",

  pendiente: "Pendiente",

  aprobada: "Aprobada",

  rechazada: "Rechazada",

  cancelacion_pendiente: "CancelaciÃ³n pendiente",

  cancelacion_rechazada: "CancelaciÃ³n rechazada",

};



const PENDING_SOLICITUD_KEY = "pendingSolicitudId";

const PREFS_STORAGE_KEY = "spmPreferences";

const DEFAULT_PREFERENCES = {

  emailAlerts: true,

  realtimeToasts: true,

  approvalDigest: false,

  digestHour: "08:30",

  theme: "auto",

  density: "comfortable",

  rememberFilters: true,

  keyboardShortcuts: false,

};



const FILTER_STORAGE_PREFIX = "spmFilters:";

const KNOWN_FILTER_KEYS = ["adminUsers", "adminMateriales", "adminSolicitudes"];

const SYSTEM_THEME_MEDIA = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

let systemThemeListener = null;

let keyboardHandler = null;



function storageKeyForFilters(key) {

  return `${FILTER_STORAGE_PREFIX}${key}`;

}



function loadStoredFilters(key, fallback = {}) {

  if (!state.preferences?.rememberFilters) {

    return { ...fallback };

  }

  try {

    const raw = localStorage.getItem(storageKeyForFilters(key));

    if (!raw) {

      return { ...fallback };

    }

    const parsed = JSON.parse(raw);

    return { ...fallback, ...parsed };

  } catch (_err) {

    return { ...fallback };

  }

}



function saveStoredFilters(key, value) {

  if (!state.preferences?.rememberFilters) {

    localStorage.removeItem(storageKeyForFilters(key));

    return;

  }

  try {

    localStorage.setItem(storageKeyForFilters(key), JSON.stringify(value));

  } catch (_err) {

    console.warn("No se pudieron guardar filtros para", key);

  }

}



function clearStoredFilters(key) {

  localStorage.removeItem(storageKeyForFilters(key));

}



function clearAllStoredFilters() {

  KNOWN_FILTER_KEYS.forEach((key) => clearStoredFilters(key));

}



function statusBadge(status) {

  const normalized = (status || "").toLowerCase();

  const fallback = normalized ? normalized.replace(/_/g, " ") : "â€”";

  const label = STATUS_LABELS[normalized] || fallback;

  const pretty = STATUS_LABELS[normalized]

    ? label

    : label.charAt(0).toUpperCase() + label.slice(1);

  return `<span class="status-pill status-${normalized || "desconocido"}">${pretty}</span>`;

}



const DEFAULT_CENTROS = ["1008", "1050", "1500"];



const DEFAULT_ALMACENES_VIRTUALES = [

  { id: "AV-CENTRAL", label: "AV-CENTRAL - AlmacÃ©n Central" },

  { id: "AV-MANT", label: "AV-MANT - DepÃ³sito de Mantenimiento" },

  { id: "AV-REP", label: "AV-REP - Repuestos CrÃ­ticos" },

  { id: "AV-SERV", label: "AV-SERV - Servicios Industriales" },

];



const MATERIAL_SUGGESTION_LIMIT = 100000;

// ============================================================================
// Funciones para búsqueda de materiales en agregar-materiales.html
// ============================================================================

let materialSearchCache = {};

/**
 * Realiza búsqueda de materiales por código
 */
async function searchMaterialsByCode(codigo) {
  if (!codigo || codigo.trim().length === 0) {
    return [];
  }
  
  const cacheKey = `code_${codigo}`;
  if (materialSearchCache[cacheKey]) {
    return materialSearchCache[cacheKey];
  }
  
  try {
    const params = new URLSearchParams({
      codigo: codigo.trim(),
      limit: '1000'
    });
    const result = await api(`/materiales?${params.toString()}`);
    if (Array.isArray(result)) {
      materialSearchCache[cacheKey] = result;
      return result;
    }
  } catch (err) {
    console.error("Error searching materials by code:", err);
  }
  return [];
}

/**
 * Realiza búsqueda de materiales por descripción
 */
async function searchMaterialsByDescription(descripcion) {
  if (!descripcion || descripcion.trim().length === 0) {
    return [];
  }
  
  const cacheKey = `desc_${descripcion}`;
  if (materialSearchCache[cacheKey]) {
    return materialSearchCache[cacheKey];
  }
  
  try {
    const params = new URLSearchParams({
      descripcion: descripcion.trim(),
      limit: '1000'
    });
    const result = await api(`/materiales?${params.toString()}`);
    if (Array.isArray(result)) {
      materialSearchCache[cacheKey] = result;
      return result;
    }
  } catch (err) {
    console.error("Error searching materials by description:", err);
  }
  return [];
}

/**
 * Muestra sugerencias en el dropdown
 */
function showMaterialSuggestions(materials, targetDropdown) {
  if (!targetDropdown) return;

  targetDropdown.innerHTML = '';

  if (!materials || materials.length === 0) {
    targetDropdown.classList.add('hide');
    targetDropdown.style.display = 'none';
    return;
  }

  targetDropdown.classList.remove('hide');
  targetDropdown.style.display = 'block';

  materials.slice(0, 1000).forEach((material) => {
    const div = document.createElement('div');
    div.style.padding = '8px 12px';
    div.style.cursor = 'pointer';
    div.style.borderBottom = '1px solid var(--border-default)';
    div.style.fontSize = '14px';
    div.style.color = 'var(--text-primary)';
    div.onmouseover = () => {
      div.style.background = 'var(--primary)';
      div.style.color = 'white';
    };
    div.onmouseout = () => {
      div.style.background = 'transparent';
      div.style.color = 'var(--text-primary)';
    };
    
    const price = material.precio_usd ? formatCurrency(material.precio_usd) : 'N/A';
    div.textContent = `${material.codigo} - ${material.descripcion} - ${price}`;
    
    div.addEventListener('click', () => {
      selectMaterial(material, targetDropdown.id === 'suggestCode' ? 'code' : 'desc');
    });

    targetDropdown.appendChild(div);
  });
}

/**
 * Selecciona un material
 */
function selectMaterial(material, source) {
  if (!window.materialPageState) {
    window.materialPageState = {};
  }
  
  window.materialPageState.selected = material;
  
  // Actualizar el input con el valor seleccionado
  if (source === 'code') {
    const codeInput = document.getElementById('codeSearch');
    if (codeInput) {
      codeInput.value = material.codigo;
      const suggestCode = document.getElementById('suggestCode');
      if (suggestCode) {
        suggestCode.classList.add('hide');
        suggestCode.style.display = 'none';
      }
    }
  } else {
    const descInput = document.getElementById('descSearch');
    if (descInput) {
      descInput.value = material.descripcion;
      const suggestDesc = document.getElementById('suggestDesc');
      if (suggestDesc) {
        suggestDesc.classList.add('hide');
        suggestDesc.style.display = 'none';
      }
    }
  }
  
  // Habilitar botón de descripción ampliada
  const btnDetail = document.getElementById('btnShowMaterialDetail');
  if (btnDetail) {
    btnDetail.disabled = false;
  }
}

/**
 * Abre modal con la descripción ampliada
 */
function openMaterialDetailModal() {
  if (!window.materialPageState || !window.materialPageState.selected) {
    toast("Por favor selecciona un material primero");
    return;
  }
  
  const material = window.materialPageState.selected;
  const modal = document.getElementById('materialDetailModal');
  const title = document.getElementById('materialDetailTitle');
  const body = document.getElementById('materialDetailBody');
  
  if (modal && title && body) {
    title.textContent = `${material.codigo} - ${material.descripcion}`;
    body.textContent = material.descripcion_larga || "No hay descripción disponible";
    modal.style.display = 'flex';
  }
}

/**
 * Cierra modal de descripción ampliada
 */
function closeMaterialDetailModal() {
  const modal = document.getElementById('materialDetailModal');
  if (modal) {
    modal.style.display = 'none';
  }
}

/**
 * Agrega material al carrito
 */
function addMaterialItem() {
  if (!window.materialPageState || !window.materialPageState.selected) {
    toast("Por favor selecciona un material");
    return;
  }
  
  if (!window.materialPageState.items) {
    window.materialPageState.items = [];
  }
  
  const material = window.materialPageState.selected;
  
  // Verificar si ya existe en el carrito
  const existing = window.materialPageState.items.find(item => item.codigo === material.codigo);
  
  if (existing) {
    toast("Este material ya está en el carrito");
    return;
  }
  
  // Agregar al carrito
  window.materialPageState.items.push({
    codigo: material.codigo,
    descripcion: material.descripcion,
    unidad: material.unidad || 'UNI',
    precio_unitario: material.precio_usd || 0,
    cantidad: 1,
    descripcion_larga: material.descripcion_larga
  });
  
  // Actualizar tabla y total
  renderMaterialsCart();
  
  // Limpiar búsqueda
  const codeInput = $('#codeSearch');
  const descInput = $('#descSearch');
  if (codeInput) codeInput.value = '';
  if (descInput) descInput.value = '';
  const suggestCode = document.getElementById('suggestCode');
  const suggestDesc = document.getElementById('suggestDesc');
  if (suggestCode) {
    suggestCode.classList.add('hide');
    suggestCode.style.display = 'none';
  }
  if (suggestDesc) {
    suggestDesc.classList.add('hide');
    suggestDesc.style.display = 'none';
  }
  
  window.materialPageState.selected = null;
  
  const btnDetail = $('#btnShowMaterialDetail');
  if (btnDetail) btnDetail.disabled = true;
  
  toast("Material agregado al carrito", true);
}

/**
 * Renderiza la tabla del carrito
 */
function renderMaterialsCart() {
  const table = $('#tbl');
  if (!table) return;
  
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  
  if (!window.materialPageState || !window.materialPageState.items) {
    tbody.innerHTML = '';
    return;
  }
  
  tbody.innerHTML = '';
  let total = 0;
  
  window.materialPageState.items.forEach((item, idx) => {
    const row = document.createElement('tr');
    
    const itemTotal = (item.precio_unitario || 0) * (item.cantidad || 1);
    total += itemTotal;
    
    row.innerHTML = `
      <td>${escapeHtml(item.codigo)}</td>
      <td>${escapeHtml(item.descripcion)}</td>
      <td>${escapeHtml(item.unidad)}</td>
      <td>${formatCurrency(item.precio_unitario || 0)}</td>
      <td>
        <input type="number" class="material-quantity" value="${item.cantidad}" 
               onchange="updateMaterialQuantity(${idx}, this.value)" min="1" />
      </td>
      <td>${formatCurrency(itemTotal)}</td>
      <td>
        <button class="btn btn--small" onclick="removeMaterialItem(${idx})">Eliminar</button>
      </td>
    `;
    
    tbody.appendChild(row);
  });
  
  const cartTotal = $('#cartTotal');
  if (cartTotal) {
    cartTotal.textContent = formatCurrency(total);
  }
}

/**
 * Actualiza la cantidad de un material en el carrito
 */
function updateMaterialQuantity(idx, newQuantity) {
  if (!window.materialPageState || !window.materialPageState.items) return;
  
  const quantity = Math.max(1, parseInt(newQuantity) || 1);
  window.materialPageState.items[idx].cantidad = quantity;
  renderMaterialsCart();
}

/**
 * Elimina un material del carrito
 */
function removeMaterialItem(idx) {
  if (!window.materialPageState || !window.materialPageState.items) return;
  
  window.materialPageState.items.splice(idx, 1);
  renderMaterialsCart();
  toast("Material eliminado", true);
}

/**
 * Inicializa la página de agregar materiales
 */
function initAddMaterialsPage() {
  console.log('Inicializando página de agregar materiales...');
  
  if (!window.materialPageState) {
    window.materialPageState = {
      items: [],
      selected: null
    };
  }
  
  // Obtener elementos
  const codeSearch = document.getElementById('codeSearch');
  const descSearch = document.getElementById('descSearch');
  const suggestCode = document.getElementById('suggestCode');
  const suggestDesc = document.getElementById('suggestDesc');
  const btnAdd = document.getElementById('btnAdd');
  const btnShowMaterialDetail = document.getElementById('btnShowMaterialDetail');

  // Aseguramos que los contenedores permitan posicionar correctamente las sugerencias
  if (codeSearch && codeSearch.parentElement) {
    codeSearch.parentElement.classList.add('searchbox');
  }
  if (descSearch && descSearch.parentElement) {
    descSearch.parentElement.classList.add('searchbox');
  }

  console.log('Elementos encontrados:', {
    codeSearch: !!codeSearch,
    descSearch: !!descSearch,
    suggestCode: !!suggestCode,
    suggestDesc: !!suggestDesc,
    btnAdd: !!btnAdd,
    btnShowMaterialDetail: !!btnShowMaterialDetail
  });
  
  // Event listeners para búsqueda por código
  if (codeSearch) {
    codeSearch.addEventListener('input', async (e) => {
      const value = e.target.value.trim();
      console.log('Búsqueda por código:', value);

      if (value.length === 0) {
        if (suggestCode) {
          suggestCode.classList.add('hide');
          suggestCode.style.display = 'none';
        }
        return;
      }

      if (value.length < 1) return;
      
      const materials = await searchMaterialsByCode(value);
      console.log('Resultados encontrados:', materials.length);
      showMaterialSuggestions(materials, suggestCode);
    });
  }
  
  // Event listeners para búsqueda por descripción
  if (descSearch) {
    descSearch.addEventListener('input', async (e) => {
      const value = e.target.value.trim();
      console.log('Búsqueda por descripción:', value);

      if (value.length === 0) {
        if (suggestDesc) {
          suggestDesc.classList.add('hide');
          suggestDesc.style.display = 'none';
        }
        return;
      }

      if (value.length < 2) return;
      
      const materials = await searchMaterialsByDescription(value);
      console.log('Resultados encontrados:', materials.length);
      showMaterialSuggestions(materials, suggestDesc);
    });
  }
  
  // Botón agregar
  if (btnAdd) {
    btnAdd.addEventListener('click', addMaterialItem);
  }
  
  // Botón descripción ampliada
  if (btnShowMaterialDetail) {
    btnShowMaterialDetail.addEventListener('click', openMaterialDetailModal);
  }
  
  // Renderizar carrito inicial
  renderMaterialsCart();
  
  // Inicializar validación visual en tiempo real (PROPUESTA 8)
  initMaterialsValidation();
  
  console.log('Página de agregar materiales inicializada correctamente');
}

// ============================================================================
// Fin de funciones para búsqueda de materiales
// ============================================================================



const ADMIN_CONFIG_FIELDS = {

  centros: ["codigo", "nombre", "descripcion", "notas", "activo"],

  almacenes: ["codigo", "nombre", "centro_codigo", "descripcion", "activo"],

  roles: ["nombre", "descripcion", "activo"],

  puestos: ["nombre", "descripcion", "activo"],

  sectores: ["nombre", "descripcion", "activo"],

};



const ADMIN_CONFIG_TABLE_FIELDS = {

  centros: ["codigo", "nombre", "descripcion", "notas", "activo"],

  almacenes: ["codigo", "nombre", "centro_codigo", "descripcion", "activo"],

  roles: ["nombre", "descripcion", "activo"],

  puestos: ["nombre", "descripcion", "activo"],

  sectores: ["nombre", "descripcion", "activo"],

};



const ADMIN_CONFIG_LABELS = {

  centros: "centro logÃ­stico",

  almacenes: "almacÃ©n virtual",

  roles: "rol",

  puestos: "puesto",

  sectores: "sector",

};



const CATALOG_KEYS = ["centros", "almacenes", "roles", "puestos", "sectores"];



function getCatalogItems(resource, { activeOnly = true } = {}) {

  if (!resource) {

    return [];

  }

  const items = Array.isArray(state.catalogs?.[resource]) ? state.catalogs[resource] : [];

  if (!activeOnly) {

    return [...items];

  }

  return items.filter((item) => item && item.activo !== false);

}



function setCatalogItems(resource, items) {

  if (!resource) {

    return;

  }

  state.catalogs[resource] = Array.isArray(items) ? items : [];

  refreshCatalogConsumers(resource);

}



function ensureCatalogDefaults(data = {}) {

  CATALOG_KEYS.forEach((key) => {

    if (!Array.isArray(data[key])) {

      data[key] = [];

    }

  });

  return data;

}



function updateDatalist(nodeId, values) {

  const node = document.getElementById(nodeId);

  if (!node) {

    return;

  }

  const unique = Array.from(new Set(values.filter(Boolean)));

  node.innerHTML = unique.map((value) => `<option value="${escapeHtml(value)}"></option>`).join("");

}



function refreshCatalogConsumers(resource = null) {

  const targets = resource ? [resource] : CATALOG_KEYS;

  if (targets.includes("roles")) {

    updateDatalist("catalogRolesList", getCatalogItems("roles", { activeOnly: true }).map((item) => item.nombre));

  }

  if (targets.includes("puestos")) {

    updateDatalist("catalogPuestosList", getCatalogItems("puestos", { activeOnly: true }).map((item) => item.nombre));

  }

  if (targets.includes("sectores")) {

    updateDatalist("catalogSectoresList", getCatalogItems("sectores", { activeOnly: true }).map((item) => item.nombre));

  }

}



function logCatalogWarnings(resource, warnings) {

  if (!Array.isArray(warnings) || !warnings.length) {

    return;

  }

  warnings.forEach((warning) => {

    if (!warning) {

      return;

    }

    const target = warning.resource || resource || "catalogos";

    const message = warning.message || (typeof warning === "string" ? warning : JSON.stringify(warning));

    console.info("[catalogos] aviso", { resource: target, message });

  });

}



async function loadCatalogData(resource = null, { silent = false, includeInactive = false } = {}) {

  if (!state.me) {

    return null;

  }

  try {

    const params = new URLSearchParams();

    if (includeInactive) {

      params.set("include_inactive", "1");

    }

    if (resource) {

      const endpoint = params.size ? `/catalogos/${resource}?${params.toString()}` : `/catalogos/${resource}`;

      const resp = await api(endpoint);

      if (!resp?.ok) {

        throw new Error(resp?.error?.message || "No se pudo cargar el catalogo");

      }

      logCatalogWarnings(resource, resp.warnings);

      setCatalogItems(resource, resp.items || []);

      if (!silent) {

        toast(`Cat?logo de ${adminConfigLabel(resource)} actualizado`, true);

      }

      return resp.items || [];

    }

    const endpoint = params.size ? `/catalogos?${params.toString()}` : "/catalogos";

    const resp = await api(endpoint);

    if (!resp?.ok) {

      throw new Error(resp?.error?.message || "No se pudo cargar la configuracion");

    }

    logCatalogWarnings(null, resp.warnings);

    const normalized = ensureCatalogDefaults(resp.data || {});

    CATALOG_KEYS.forEach((key) => {

      setCatalogItems(key, normalized[key]);

    });

    if (!silent) {

      toast("Cat?logos sincronizados", true);

    }

    return normalized;

  } catch (err) {

    console.error(err);

    if (!silent) {

      toast(err.message || "No se pudieron cargar los catalogos");

    }

    return null;

  }

}



function catalogueOptionLabel(code, name, extra) {

  const parts = [code];

  const printableName = (name || "").trim();

  if (printableName && printableName.toUpperCase() !== String(code || "").toUpperCase()) {

    parts.push(printableName);

  }

  if (extra) {

    parts.push(extra);

  }

  return parts.join(" - ");

}



function canViewTeamRequests() {

  try {
    const posicion = (state?.me?.posicion || "").toLowerCase();
    const role = (state?.me?.rol || "").toLowerCase();
    return posicion.includes("jefe") || posicion.includes("gerente") || role.includes("jefe") || role.includes("gerente");
  } catch (e) {
    console.warn("Error checking team requests permission:", e);
    return false;
  }

}



function configureRequestsMenu() {

  try {
    const requestsMenu = document.querySelector('[data-menu="solicitudes"] .app-submenu');

    if (!requestsMenu) {
      return;
    }

    // Always show "Mis solicitudes" and "Crear solicitud"
    let menuHtml = `
      <a href="mis-solicitudes.html" class="app-submenu__link" role="menuitem">Mis solicitudes</a>
      <a href="crear-solicitud.html" class="app-submenu__link" role="menuitem">Crear solicitud</a>
    `;

    // Add "Solicitudes de mi Equipo" for managers
    if (canViewTeamRequests()) {
      menuHtml += `<a href="equipo-solicitudes.html" class="app-submenu__link" role="menuitem">Solicitudes de mi Equipo</a>`;
    }

    requestsMenu.innerHTML = menuHtml;
  } catch (e) {
    console.warn("Error configuring requests menu:", e);
  }

}



// Nueva funcionalidad para la pÃ¡gina de solicitudes del equipo

async function loadEquipoSolicitudes() {

  try {

    const response = await api("/solicitudes/equipo");

    if (!response.ok) {

      throw new Error(response.error?.message || "Error al cargar solicitudes del equipo");

    }



    const solicitudes = response.items || [];

    renderEquipoSolicitudes(solicitudes);

  } catch (err) {

    console.error(err);

    toast(err.message || "Error al cargar solicitudes del equipo");

  }

}



function renderEquipoSolicitudes(solicitudes) {

  const tbody = $("#equipoSolicitudesTableBody");

  if (!tbody) return;



  tbody.innerHTML = "";



  if (solicitudes.length === 0) {

    const emptyRow = document.createElement("tr");

    emptyRow.innerHTML = `<td colspan="8" style="text-align: center; padding: 2rem;">No hay solicitudes de tu equipo</td>`;

    tbody.appendChild(emptyRow);

    return;

  }



  solicitudes.forEach(solicitud => {

    const row = document.createElement("tr");



    const fecha = formatDateTime(solicitud.created_at);

    const estado = getEstadoLabel(solicitud.status);

    const total = formatCurrency(solicitud.total_monto || 0);

    const solicitante = solicitud.solicitante || solicitud.id_usuario || "Desconocido";



    row.innerHTML = `

      <td>${solicitud.id}</td>

      <td>${fecha}</td>

      <td>${solicitante}</td>

      <td>${solicitud.centro || ""}</td>

      <td><span class="status status--${solicitud.status}">${estado}</span></td>

      <td>${solicitud.planner_nombre || "No asignado"}</td>

      <td>${total}</td>

      <td>

        <button type="button" class="btn btn--small" onclick="openSolicitudDetail(${solicitud.id})">

          Ver detalle

        </button>

      </td>

    `;



    tbody.appendChild(row);

  });

}



function getEstadoLabel(status) {

  const labels = {

    "draft": "Borrador",

    "approved": "Aprobada",

    "en_tratamiento": "En tratamiento",

    "completed": "Completada",

    "cancelled": "Cancelada"

  };

  return labels[status] || status;

}



// InicializaciÃ³n de la pÃ¡gina de equipo

function initEquipoSolicitudesPage() {

  loadEquipoSolicitudes();



  // Configurar filtros

  const filterBtn = $("#equipoFilterBtn");

  if (filterBtn) {

    filterBtn.addEventListener("click", () => {

      loadEquipoSolicitudes(); // Por ahora recarga todo, despuÃ©s se puede filtrar en cliente

    });

  }

}



// Reportes functions

async function loadReportesEstadisticas() {

  try {

    const response = await api("/reportes/estadisticas");

    if (!response.ok) {

      throw new Error(response.error?.message || "Error al cargar estadÃ­sticas");

    }



    const data = response.estadisticas;

    renderEstadisticas(data);



    // Renderizar grÃ¡ficos si Chart.js estÃ¡ disponible

    if (typeof Chart !== 'undefined') {

      renderEstadoChart(response.por_estado || []);

      renderCentroChart(response.por_centro || []);

      renderTendenciaChart(response.tendencia_mensual || []);

    }

  } catch (err) {

    console.error(err);

    toast(err.message || "Error al cargar estadÃ­sticas");

  }

}



function renderEstadisticas(data) {

  const totalSpan = $("#totalSolicitudes");

  const activasSpan = $("#solicitudesActivas");

  const completadasSpan = $("#solicitudesCompletadas");

  const montoSpan = $("#montoTotal");



  if (totalSpan) totalSpan.textContent = data.total_solicitudes || 0;

  if (activasSpan) activasSpan.textContent = data.solicitudes_activas || 0;

  if (completadasSpan) completadasSpan.textContent = data.solicitudes_completadas || 0;

  if (montoSpan) montoSpan.textContent = formatCurrency(data.monto_total || 0);

}



function renderEstadoChart(data) {

  const ctx = $("#estadoChart");

  if (!ctx) return;



  const labels = data.map(item => getEstadoLabel(item.estado));

  const values = data.map(item => item.cantidad);



  new Chart(ctx, {

    type: 'pie',

    data: {

      labels: labels,

      datasets: [{

        data: values,

        backgroundColor: [

          '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'

        ]

      }]

    },

    options: {

      responsive: true,

      plugins: {

        legend: {

          position: 'bottom',

        }

      }

    }

  });

}



function renderCentroChart(data) {

  const ctx = $("#centroChart");

  if (!ctx) return;



  const labels = data.map(item => item.centro || 'Sin centro');

  const values = data.map(item => item.cantidad);



  new Chart(ctx, {

    type: 'bar',

    data: {

      labels: labels,

      datasets: [{

        label: 'Solicitudes',

        data: values,

        backgroundColor: '#36A2EB'

      }]

    },

    options: {

      responsive: true,

      scales: {

        y: {

          beginAtZero: true

        }

      }

    }

  });

}



function renderTendenciaChart(data) {

  const ctx = $("#tendenciaChart");

  if (!ctx) return;



  const labels = data.map(item => item.mes);

  const values = data.map(item => item.cantidad);



  new Chart(ctx, {

    type: 'line',

    data: {

      labels: labels,

      datasets: [{

        label: 'Solicitudes',

        data: values,

        borderColor: '#FF6384',

        backgroundColor: 'rgba(255, 99, 132, 0.2)',

        tension: 0.1

      }]

    },

    options: {

      responsive: true,

      scales: {

        y: {

          beginAtZero: true

        }

      }

    }

  });

}



async function generarReporte() {

  const tipo = $("#reporteTipo")?.value || "solicitudes";

  const formato = $("#reporteFormato")?.value || "excel";

  const fechaDesde = $("#reporteFechaDesde")?.value || "";

  const fechaHasta = $("#reporteFechaHasta")?.value || "";



  try {

    const params = new URLSearchParams({

      tipo,

      formato,

      fecha_desde: fechaDesde,

      fecha_hasta: fechaHasta

    });



    // Crear un enlace temporal para descargar

    const link = document.createElement('a');

    link.href = `${API}/reportes/exportar?${params}`;

    link.download = `reporte.${formato}`;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);



    toast("Reporte generado exitosamente", true);

  } catch (err) {

    console.error(err);

    toast("Error al generar el reporte");

  }

}



// InicializaciÃ³n de la pÃ¡gina de reportes

function initReportesPage() {

  loadReportesEstadisticas();



  // Configurar botones

  const generarBtn = $("#generarReporteBtn");

  if (generarBtn) {

    generarBtn.addEventListener("click", generarReporte);

  }



  const exportarBtn = $("#exportarDatosBtn");

  if (exportarBtn) {

    exportarBtn.addEventListener("click", () => {

      // Por ahora mismo que generar reporte

      generarReporte();

    });

  }
}

// ===== TABLA DE MATERIALES AGREGADOS =====
// Array global para almacenar materiales agregados
window.agregatedMaterials = [];

function addMaterialToList() {
  const materialSelect = document.getElementById('materialSelect');
  const quantityInput = document.getElementById('materialQuantity');
  const priceInput = document.getElementById('materialPrice');
  
  // Validaciones
  if (!materialSelect.value || !materialSelect.value.trim()) {
    toast('Selecciona un material', false);
    return;
  }
  
  if (!quantityInput.value || parseFloat(quantityInput.value) < 1) {
    toast('La cantidad debe ser mayor a 0', false);
    return;
  }
  
  if (!priceInput.value || parseFloat(priceInput.value) < 0) {
    toast('El precio debe ser válido', false);
    return;
  }
  
  // Obtener valores
  const material = materialSelect.value;
  const quantity = parseFloat(quantityInput.value);
  const price = parseFloat(priceInput.value);
  const subtotal = quantity * price;
  
  // Agregar a array
  window.agregatedMaterials.push({
    material: material,
    quantity: quantity,
    price: price,
    subtotal: subtotal
  });
  
  // Actualizar tabla
  updateMaterialsTable();
  
  // Limpiar campos
  materialSelect.value = '';
  quantityInput.value = '';
  priceInput.value = '';
  materialSelect.focus();
  
  // Mostrar feedback
  toast(`Material agregado: ${material}`, true);
}

function removeMaterialRow(index) {
  if (index >= 0 && index < window.agregatedMaterials.length) {
    const removedMaterial = window.agregatedMaterials[index].material;
    window.agregatedMaterials.splice(index, 1);
    updateMaterialsTable();
    toast(`Material removido: ${removedMaterial}`, true);
  }
}

/**
 * PROPUESTA 4: Incrementa la cantidad de un material en la tabla (botón +)
 */
function incrementQuantity(index) {
  if (index >= 0 && index < window.agregatedMaterials.length) {
    window.agregatedMaterials[index].quantity += 1;
    updateMaterialsTable();
  }
}

/**
 * PROPUESTA 4: Decrementa la cantidad de un material en la tabla (botón -)
 * Mínimo: 1 unidad
 */
function decrementQuantity(index) {
  if (index >= 0 && index < window.agregatedMaterials.length) {
    if (window.agregatedMaterials[index].quantity > 1) {
      window.agregatedMaterials[index].quantity -= 1;
      updateMaterialsTable();
    } else {
      toast('La cantidad mínima es 1', false);
    }
  }
}

/**
 * Actualiza la cantidad de un material editada manualmente
 */
function updateQuantity(index, newQuantity) {
  if (index >= 0 && index < window.agregatedMaterials.length) {
    const qty = parseInt(newQuantity) || 1;
    if (qty >= 1) {
      window.agregatedMaterials[index].quantity = qty;
      updateMaterialsTable();
    } else {
      toast('La cantidad debe ser mayor a 0', false);
      updateMaterialsTable();
    }
  }
}

function clearAllMaterials() {
  if (window.agregatedMaterials.length === 0) {
    toast('No hay materiales para limpiar', false);
    return;
  }
  
  if (confirm('¿Está seguro que desea eliminar todos los materiales?')) {
    window.agregatedMaterials = [];
    updateMaterialsTable();
    toast('Todos los materiales fueron eliminados', true);
  }
}

function updateMaterialsTable() {
  const tbody = document.getElementById('materialsTableBody');
  const countSpan = document.getElementById('materialsCount');
  const totalSpan = document.getElementById('materialsTotal');
  
  if (!tbody) return;
  
  // Actualizar contador
  countSpan.textContent = window.agregatedMaterials.length;
  
  // Si no hay materiales, mostrar mensaje
  if (window.agregatedMaterials.length === 0) {
    tbody.innerHTML = '<tr style="text-align: center; color: #9ca3af;"><td colspan="5" style="padding: 24px; border: none;">Sin materiales agregados</td></tr>';
    totalSpan.textContent = '$0.00';
    return;
  }
  
  // Generar filas de tabla
  let html = '';
  let total = 0;
  
  window.agregatedMaterials.forEach((item, index) => {
    const subtotal = item.quantity * item.price;
    total += subtotal;
    const unit = item.unit || 'u.';
    
    html += `
      <tr style="border-bottom: 1px solid #e5e7eb; hover-background: #f9fafb;">
        <td style="padding: 12px; text-align: left; border: none; color: #111827;">
          <div style="font-weight: 600;">${item.material}</div>
          <div style="font-size: 0.8rem; color: #6b7280;">SAP: ${item.codigo_sap || '--'}</div>
        </td>
        <td style="padding: 12px; text-align: center; border: none; color: #111827;">
          <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
            <button type="button" onclick="decrementQuantity(${index})" style="background: #e5e7eb; color: #374151; border: 1px solid #d1d5db; border-radius: 4px; padding: 4px 8px; cursor: pointer; font-weight: 600; font-size: 0.85rem; transition: all 0.2s;" onmouseover="this.style.background='#d1d5db'" onmouseout="this.style.background='#e5e7eb'">−</button>
            <input type="number" value="${item.quantity}" min="1" style="width: 50px; text-align: center; border: 1px solid #d1d5db; padding: 4px; border-radius: 4px; font-weight: 600;" onchange="updateQuantity(${index}, this.value)">
            <button type="button" onclick="incrementQuantity(${index})" style="background: #e5e7eb; color: #374151; border: 1px solid #d1d5db; border-radius: 4px; padding: 4px 8px; cursor: pointer; font-weight: 600; font-size: 0.85rem; transition: all 0.2s;" onmouseover="this.style.background='#d1d5db'" onmouseout="this.style.background='#e5e7eb'">+</button>
          </div>
        </td>
        <td style="padding: 12px; text-align: right; border: none; color: #111827;">
          <div style="font-weight: 600;">$${item.price.toFixed(2)}</div>
          <div style="font-size: 0.8rem; color: #6b7280;">${unit}</div>
        </td>
        <td style="padding: 12px; text-align: right; border: none; color: #111827; font-weight: 600;">$${subtotal.toFixed(2)}</td>
        <td style="padding: 12px; text-align: center; border: none;">
          <button type="button" onclick="removeMaterialRow(${index})" style="background: #ef4444; color: white; border: none; border-radius: 4px; padding: 6px 12px; cursor: pointer; font-weight: 500; font-size: 0.85rem; transition: background 0.2s;" onmouseover="this.style.background='#dc2626'" onmouseout="this.style.background='#ef4444'">
            🗑️ Eliminar
          </button>
        </td>
      </tr>
    `;
  });
  
  tbody.innerHTML = html;
  totalSpan.textContent = `$${total.toFixed(2)}`;
}

// ===== VALIDACIÓN VISUAL EN TIEMPO REAL (PROPUESTA 8) =====

/**
 * Estado de validación global
 */
const validationState = {
  material: null,
  quantity: null,
  price: null
};

/**
 * Valida el campo de Material
 */
function validateMaterialField() {
  const field = document.getElementById('materialSelect');
  const indicator = document.getElementById('materialIndicator');
  const errorDiv = document.getElementById('materialError');
  const value = field?.value?.trim();
  
  if (!field) return;
  
  if (!value) {
    validationState.material = false;
    field.style.borderColor = '#fca5a5';
    field.style.backgroundColor = '#fef2f2';
    indicator.textContent = '🔴';
    indicator.style.display = 'inline';
    errorDiv.textContent = 'Selecciona un material';
    errorDiv.style.display = 'block';
  } else if (value.length < 2) {
    validationState.material = false;
    field.style.borderColor = '#fbbf24';
    field.style.backgroundColor = '#fffbeb';
    indicator.textContent = '⚠️';
    indicator.style.display = 'inline';
    errorDiv.textContent = 'Material inválido o muy corto';
    errorDiv.style.display = 'block';
  } else {
    validationState.material = true;
    field.style.borderColor = '#86efac';
    field.style.backgroundColor = '#f0fdf4';
    indicator.textContent = '✅';
    indicator.style.display = 'inline';
    errorDiv.style.display = 'none';
  }
  
  updateAddButtonState();
}

/**
 * Valida el campo de Cantidad
 */
function validateQuantityField() {
  const field = document.getElementById('materialQuantity');
  const indicator = document.getElementById('quantityIndicator');
  const errorDiv = document.getElementById('quantityError');
  const value = field?.value;
  
  if (!field) return;
  
  const numValue = parseFloat(value);
  
  if (!value || value === '') {
    validationState.quantity = false;
    field.style.borderColor = '#fca5a5';
    field.style.backgroundColor = '#fef2f2';
    indicator.textContent = '🔴';
    indicator.style.display = 'inline';
    errorDiv.textContent = 'La cantidad es requerida';
    errorDiv.style.display = 'block';
  } else if (isNaN(numValue) || numValue <= 0) {
    validationState.quantity = false;
    field.style.borderColor = '#fca5a5';
    field.style.backgroundColor = '#fef2f2';
    indicator.textContent = '🔴';
    indicator.style.display = 'inline';
    errorDiv.textContent = 'Cantidad debe ser mayor a 0';
    errorDiv.style.display = 'block';
  } else if (numValue < 1) {
    validationState.quantity = false;
    field.style.borderColor = '#fbbf24';
    field.style.backgroundColor = '#fffbeb';
    indicator.textContent = '⚠️';
    indicator.style.display = 'inline';
    errorDiv.textContent = 'Cantidad muy baja (mínimo 1)';
    errorDiv.style.display = 'block';
  } else if (!Number.isInteger(numValue)) {
    validationState.quantity = false;
    field.style.borderColor = '#fbbf24';
    field.style.backgroundColor = '#fffbeb';
    indicator.textContent = '⚠️';
    indicator.style.display = 'inline';
    errorDiv.textContent = 'Cantidad debe ser un número entero';
    errorDiv.style.display = 'block';
  } else {
    validationState.quantity = true;
    field.style.borderColor = '#86efac';
    field.style.backgroundColor = '#f0fdf4';
    indicator.textContent = '✅';
    indicator.style.display = 'inline';
    errorDiv.style.display = 'none';
  }
  
  updateAddButtonState();
}

/**
 * Valida el campo de Precio
 */
function validatePriceField() {
  const field = document.getElementById('materialPrice');
  const indicator = document.getElementById('priceIndicator');
  const errorDiv = document.getElementById('priceError');
  const value = field?.value;
  
  if (!field) return;
  
  const numValue = parseFloat(value);
  
  if (!value || value === '') {
    validationState.price = false;
    field.style.borderColor = '#fca5a5';
    field.style.backgroundColor = '#fef2f2';
    indicator.textContent = '🔴';
    indicator.style.display = 'inline';
    errorDiv.textContent = 'El precio es requerido';
    errorDiv.style.display = 'block';
  } else if (isNaN(numValue) || numValue < 0) {
    validationState.price = false;
    field.style.borderColor = '#fca5a5';
    field.style.backgroundColor = '#fef2f2';
    indicator.textContent = '🔴';
    indicator.style.display = 'inline';
    errorDiv.textContent = 'Precio no puede ser negativo';
    errorDiv.style.display = 'block';
  } else if (numValue === 0) {
    validationState.price = false;
    field.style.borderColor = '#fbbf24';
    field.style.backgroundColor = '#fffbeb';
    indicator.textContent = '⚠️';
    indicator.style.display = 'inline';
    errorDiv.textContent = 'Precio es $0 (¿sin costo?)';
    errorDiv.style.display = 'block';
  } else if (numValue > 100000) {
    validationState.price = false;
    field.style.borderColor = '#fbbf24';
    field.style.backgroundColor = '#fffbeb';
    indicator.textContent = '⚠️';
    indicator.style.display = 'inline';
    errorDiv.textContent = 'Precio parece muy alto (>$100k)';
    errorDiv.style.display = 'block';
  } else {
    validationState.price = true;
    field.style.borderColor = '#86efac';
    field.style.backgroundColor = '#f0fdf4';
    indicator.textContent = '✅';
    indicator.style.display = 'inline';
    errorDiv.style.display = 'none';
  }
  
  updateAddButtonState();
}

/**
 * Actualiza el estado del botón Agregar según validaciones
 */
function updateAddButtonState() {
  const btn = document.getElementById('btnAddMaterial');
  if (!btn) return;
  
  const isValid = validationState.material === true && 
                  validationState.quantity === true && 
                  validationState.price === true;
  
  if (isValid) {
    btn.disabled = false;
    btn.style.background = 'var(--success)';
    btn.style.color = 'white';
    btn.style.cursor = 'pointer';
    btn.style.opacity = '1';
  } else {
    btn.disabled = true;
    btn.style.background = '#d1d5db';
    btn.style.color = '#9ca3af';
    btn.style.cursor = 'not-allowed';
    btn.style.opacity = '0.6';
  }
}

/**
 * Inicializa validación en campos
 */
function initMaterialsValidation() {
  const materialField = document.getElementById('materialSelect');
  const quantityField = document.getElementById('materialQuantity');
  const priceField = document.getElementById('materialPrice');
  
  if (materialField) {
    materialField.addEventListener('blur', validateMaterialField);
  }
  if (quantityField) {
    quantityField.addEventListener('blur', validateQuantityField);
  }
  if (priceField) {
    priceField.addEventListener('blur', validatePriceField);
  }
  
  // Forzar validación inicial
  setTimeout(() => {
    validateMaterialField();
    validateQuantityField();
    validatePriceField();
  }, 100);
}

// ===== FIN VALIDACIÓN VISUAL =====

// ===== MODAL DE DESCRIPCIÓN AMPLIADA DE MATERIAL =====

/**
 * Muestra el modal con la descripción ampliada del material desde búsqueda
 */
async function showMaterialDescriptionFromSearch() {
  const sapCode = document.getElementById('materialSearchSAP')?.value.trim();
  const description = document.getElementById('materialSearchDesc')?.value.trim();
  
  if (!sapCode && !description) {
    toast('Por favor ingresa un código SAP o descripción');
    return;
  }
  
  try {
    // Buscar material con criterios
    let url = '/api/materiales?';
    if (sapCode) url += `codigo=${encodeURIComponent(sapCode)}`;
    if (description) {
      if (sapCode) url += '&';
      url += `descripcion=${encodeURIComponent(description)}`;
    }
    url += '&limit=1';
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Error buscando material');
    
    const materials = await response.json();
    if (!materials || materials.length === 0) {
      toast('Material no encontrado');
      return;
    }
    
    const material = materials[0];
    showMaterialDescriptionModal(material);
    
  } catch (error) {
    console.error('Error en showMaterialDescriptionFromSearch:', error);
    toast('Error al cargar detalles del material');
  }
}

/**
 * Muestra el modal con detalles del material
 * @param {Object} material - Objeto con propiedades del material
 */
function showMaterialDescriptionModal(material) {
  const modal = document.getElementById('materialDescriptionModal');
  if (!modal) return;
  
  // Llenar datos básicos
  document.getElementById('materialDescTitle').textContent = `${material.codigo} - ${material.descripcion}`;
  document.getElementById('materialDescCode').textContent = material.codigo || '--';
  document.getElementById('materialDescUnit').textContent = material.unidad || '--';
  document.getElementById('materialDescContent').textContent = material.descripcion_larga || 'Sin descripción disponible';
  document.getElementById('materialDescPrice').textContent = `$${(material.precio_usd || 0).toFixed(2)}`;
  
  // Guardar material actual para referencia posterior
  window.currentMaterialForModal = material;
  
  // Mostrar modal
  modal.style.display = 'flex';
  
  // Animar entrada
  const content = modal.querySelector('div > div');
  if (content) {
    content.style.animation = 'slideIn 0.3s ease-out';
  }
  
  // Cargar stock (simulado, puedes conectar a API real)
  loadMaterialStockInfo(material.codigo);
}

/**
 * Carga información de stock (puede conectarse a API real)
 * @param {string} materialCode - Código del material
 */
async function loadMaterialStockInfo(materialCode) {
  const stockDiv = document.getElementById('materialDescStock');
  if (!stockDiv) return;
  
  try {
    // Por ahora simulamos datos. En producción, esto vendría de una API
    const stockData = {
      available: Math.floor(Math.random() * 1000),
      reserved: Math.floor(Math.random() * 100),
      incoming: Math.floor(Math.random() * 500),
      warehouse: 'Centro Principal'
    };
    
    stockDiv.innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.9rem;">
        <div>
          <span style="color: #1e40af; font-weight: 500;">Disponible:</span>
          <div style="color: #10b981; font-weight: 700; font-size: 1.1rem; margin-top: 4px;">${stockData.available} unidades</div>
        </div>
        <div>
          <span style="color: #1e40af; font-weight: 500;">Reservado:</span>
          <div style="color: #f59e0b; font-weight: 600; margin-top: 4px;">${stockData.reserved} unidades</div>
        </div>
        <div>
          <span style="color: #1e40af; font-weight: 500;">En Camino:</span>
          <div style="color: #6366f1; font-weight: 600; margin-top: 4px;">${stockData.incoming} unidades</div>
        </div>
        <div>
          <span style="color: #1e40af; font-weight: 500;">Almacén:</span>
          <div style="color: #111827; font-weight: 600; margin-top: 4px;">${stockData.warehouse}</div>
        </div>
      </div>
    `;
  } catch (error) {
    console.error('Error cargando stock:', error);
    stockDiv.innerHTML = '<span style="color: #dc2626;">Error al cargar información de stock</span>';
  }
}

/**
 * Cierra el modal de descripción ampliada
 */
function closeMaterialDescriptionModal() {
  const modal = document.getElementById('materialDescriptionModal');
  if (modal) {
    modal.style.display = 'none';
  }
  window.currentMaterialForModal = null;
}

/**
 * Agrega el material mostrado en el modal directamente a la tabla
 */
function addMaterialFromModal() {
  if (!window.currentMaterialForModal) {
    toast('Material no válido');
    return;
  }
  
  const material = window.currentMaterialForModal;
  
  // Agregar directamente al array de materiales agregados
  window.agregatedMaterials.push({
    material: material.descripcion,
    codigo_sap: material.codigo,
    quantity: 1,  // Cantidad por defecto
    price: material.precio_usd || 0,
    unit: material.unidad || 'u.',
    subtotal: material.precio_usd || 0
  });
  
  // Actualizar tabla
  updateMaterialsTable();
  
  // Cerrar modal
  closeMaterialDescriptionModal();
  
  toast(`Material "${material.descripcion}" agregado exitosamente`, true);
}

// ===== FIN MODAL DE DESCRIPCIÓN AMPLIADA =====

// ===== FUNCIONES DE FILTRADO Y AUTOCOMPLETE =====

/**
 * Busca materiales directamente en la API
 */
async function filterMaterials() {
  const sapFilter = document.getElementById('materialSearchSAP')?.value.trim() || '';
  const descFilter = document.getElementById('materialSearchDesc')?.value.trim() || '';
  const categoryFilter = document.getElementById('materialSearchCategory')?.value || '';
  const sortBy = document.getElementById('sortBy')?.value || 'relevancia';

  // No hacer búsqueda si no hay criterios
  if (!sapFilter && !descFilter && !categoryFilter) {
    document.getElementById('resultsCount').textContent = 'Resultados: 0';
    document.getElementById('searchSuggestions').style.display = 'none';
    return;
  }

  try {
    // Construir URL de búsqueda - IMPORTANTE: usar q para búsqueda general
    let url = '/api/materiales?limit=10000';
    
    // Si hay SAP, usar parámetro codigo
    if (sapFilter) {
      url = `/api/materiales?codigo=${encodeURIComponent(sapFilter)}&limit=10000`;
    } 
    // Si hay descripción, usar parámetro descripcion
    else if (descFilter) {
      url = `/api/materiales?descripcion=${encodeURIComponent(descFilter)}&limit=10000`;
    }

    console.log('Buscando con URL:', url);

    const response = await fetch(url);
    if (!response.ok) {
      console.error('Error en búsqueda:', response.status);
      document.getElementById('resultsCount').textContent = 'Error en búsqueda';
      return;
    }

    let results = await response.json();
    if (!Array.isArray(results)) results = [];

    // Aplicar ordenamiento
    switch (sortBy) {
      case 'precio_asc':
        results.sort((a, b) => (a.precio_usd || 0) - (b.precio_usd || 0));
        break;
      case 'precio_desc':
        results.sort((a, b) => (b.precio_usd || 0) - (a.precio_usd || 0));
        break;
      case 'nombre_asc':
        results.sort((a, b) => a.descripcion.localeCompare(b.descripcion));
        break;
      case 'nombre_desc':
        results.sort((a, b) => b.descripcion.localeCompare(a.descripcion));
        break;
    }

    // Actualizar contador
    document.getElementById('resultsCount').textContent = `Resultados: ${results.length}`;

    // Mostrar resultados en dropdown
    showSearchResults(results);

    return results;
  } catch (error) {
    console.error('Error en filterMaterials:', error);
    document.getElementById('resultsCount').textContent = 'Error';
  }
}

/**
 * Muestra los resultados de búsqueda en un dropdown
 */
function showSearchResults(results) {
  const suggestionsDiv = document.getElementById('searchSuggestions');
  const suggestionsList = document.getElementById('suggestionsList');

  if (!suggestionsDiv || !suggestionsList) return;

  if (!results || results.length === 0) {
    suggestionsDiv.style.display = 'none';
    return;
  }

  suggestionsDiv.style.display = 'block';
  suggestionsList.innerHTML = '';

  results.slice(0, 50).forEach((material, idx) => {
    const item = document.createElement('div');
    item.style.cssText = `
      padding: 10px 12px;
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.9rem;
      transition: all 0.2s;
      margin-bottom: 4px;
    `;

    item.onmouseover = () => {
      item.style.background = '#f0f9ff';
      item.style.borderColor = '#0284c7';
    };

    item.onmouseout = () => {
      item.style.background = 'white';
      item.style.borderColor = '#e5e7eb';
    };

    item.onclick = () => {
      selectMaterialFromSearch(material);
    };

    item.innerHTML = `
      <span>
        <strong>${material.codigo}</strong> - ${material.descripcion.substring(0, 50)}
      </span>
      <span style="color: #6b7280; font-weight: 500;">$${(material.precio_usd || 0).toFixed(2)}</span>
    `;

    suggestionsList.appendChild(item);
  });

  if (results.length > 50) {
    const moreItem = document.createElement('div');
    moreItem.style.cssText = `
      padding: 10px 12px;
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 4px;
      text-align: center;
      color: #6b7280;
      font-size: 0.85rem;
    `;
    moreItem.textContent = `... y ${results.length - 50} resultados más`;
    suggestionsList.appendChild(moreItem);
  }
}

/**
 * Selecciona un material de la búsqueda y abre el modal
 */
function selectMaterialFromSearch(material) {
  showMaterialDescriptionModal(material);
  // Ocultar dropdown
  const suggestionsDiv = document.getElementById('searchSuggestions');
  if (suggestionsDiv) suggestionsDiv.style.display = 'none';
}

/**
 * Muestra sugerencias de búsquedas (detonada por oninput)
 */
function showSearchSuggestions() {
  const suggestionsDiv = document.getElementById('searchSuggestions');
  if (!suggestionsDiv) return;

  const sapValue = document.getElementById('materialSearchSAP')?.value.trim();
  const descValue = document.getElementById('materialSearchDesc')?.value.trim();

  if (sapValue || descValue) {
    // Si hay algo escrito, filtrar y mostrar resultados
    filterMaterials();
  } else {
    // Si no hay nada escrito, ocultar
    suggestionsDiv.style.display = 'none';
  }
}

/**
 * Inicializa el cache de materiales (ahora vacío, usamos API directa)
 */
function loadMaterialsCache() {
  // Cache no necesario, usamos API directa con filtros
  console.log('Autocomplete listo: buscando directamente en API');
}

/**
 * Limpia todos los filtros de búsqueda
 */
function clearSearchFilters() {
  document.getElementById('materialSearchSAP').value = '';
  document.getElementById('materialSearchDesc').value = '';
  document.getElementById('materialSearchCategory').value = '';
  document.getElementById('sortBy').value = 'relevancia';
  document.getElementById('resultsCount').textContent = 'Resultados: 0';
  document.getElementById('searchSuggestions').style.display = 'none';
}

// ===== FIN TABLA DE MATERIALES =====

// Auto-initialize pages based on detected elements
document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  // Cargar cache de materiales para autocomplete
  loadMaterialsCache();

  // Detect agregar-materiales page
  if (document.getElementById('codeSearch') && document.getElementById('btnAdd')) {
    initAddMaterialsPage();
  }

  // Finalizar página: marcar body como listo
  finalizePage();
});

// Integrar boot.js
const logoutBtn = document.querySelector('#btn-logout');
if (logoutBtn) logoutBtn.addEventListener('click', async () => { await window.API.logout(); location.href = '/index.html'; });
