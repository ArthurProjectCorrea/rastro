/* app.js — minimal shared logic of the mockup.
   Infrastructure only: read tables (JSON), simulated session, layout and display helpers.
   NEVER put business rules or hardcoded data here. */
const Mock = (() => {
  const ROOT = new URL('../', document.currentScript.src).href;
  const SESSION_KEY = 'mockup.user_id';
  const cache = {};

  /* ---------- data ---------- */
  function json(path) {
    if (!cache[path]) {
      cache[path] = fetch(ROOT + path).then((response) => {
        if (!response.ok)
          throw new Error(
            `Não foi possível carregar ${path} (${response.status})`,
          );
        return response.json();
      });
    }
    return cache[path];
  }

  /* Mock.tables('orders', 'customers') -> { orders: [...], customers: [...] } */
  async function tables(...names) {
    const lists = await Promise.all(
      names.map((name) => json(`data/${name}.json`)),
    );
    return Object.fromEntries(names.map((name, i) => [name, lists[i]]));
  }

  const byId = (list, id) => list.find((row) => row.id === Number(id)) ?? null;
  const param = (name) => new URLSearchParams(location.search).get(name);

  /* ---------- display ---------- */
  const esc = (value) =>
    String(value ?? '').replace(
      /[&<>"']/g,
      (c) =>
        ({
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#39;',
        })[c],
    );
  const currency = (n) =>
    Number(n).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  const date = (iso) => {
    const [y, m, d] = iso.split('-');
    return `${d}/${m}/${y}`;
  };
  const badge = (row) =>
    `<span class="badge badge--${esc(row.tone)}">${esc(row.name)}</span>`;

  /* Fills a <select> with the rows of a table. `placeholder` creates the "All"/"Select" option. */
  function options(select, list, label = 'name', placeholder = null) {
    const first =
      placeholder === null
        ? ''
        : `<option value="">${esc(placeholder)}</option>`;
    select.innerHTML =
      first +
      list
        .map((row) => `<option value="${row.id}">${esc(row[label])}</option>`)
        .join('');
  }

  function toast(message, target) {
    const el = document.createElement('div');
    el.className = 'toast';
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(
      () => {
        el.remove();
        if (target) location.href = new URL(target, location.href).href;
      },
      target ? 900 : 2200,
    );
  }

  function showError(error) {
    console.error(error);
    const el = document.createElement('div');
    el.className = 'error-banner';
    el.textContent = error.message || String(error);
    document.body.prepend(el);
  }

  /* ---------- simulated session (no password) ---------- */
  function userId() {
    try {
      return Number(sessionStorage.getItem(SESSION_KEY)) || null;
    } catch {
      return null;
    }
  }
  function signIn(id) {
    try {
      sessionStorage.setItem(SESSION_KEY, String(id));
    } catch {
      /* ignore */
    }
  }
  function signOut() {
    try {
      sessionStorage.removeItem(SESSION_KEY);
    } catch {
      /* ignore */
    }
    location.href = ROOT + 'screens/login.html';
  }

  /* ---------- layout ----------
     <body data-layout="app">    side menu + top bar, built from screens.json
     <body data-layout="center"> centered content (login)
     no data-layout              plain page (index) */
  async function mountLayout() {
    if (location.protocol === 'file:') {
      throw new Error(
        'Abra o mockup por um servidor local: python3 mockup/serve.py (os JSON não carregam via file://).',
      );
    }
    const mode = document.body.dataset.layout;
    if (mode === 'center') document.body.classList.add('center');
    if (mode !== 'app') return true;

    if (!userId()) {
      location.href = ROOT + 'screens/login.html';
      return false;
    }

    const [{ users }, registry] = await Promise.all([
      tables('users'),
      json('screens.json'),
    ]);
    const user = byId(users, userId());
    const current = document.body.dataset.screen;
    const items = registry.screens
      .filter((s) => s.menu)
      .map(
        (s) =>
          `<a class="menu__item${s.id === current ? ' menu__item--active' : ''}" href="${ROOT}${esc(s.file)}">${esc(s.title)}</a>`,
      )
      .join('');

    const app = document.createElement('div');
    app.className = 'app';
    app.innerHTML = `
      <aside class="menu">
        <div class="menu__brand">${esc(registry.project)}</div>
        <nav class="menu__list">${items}</nav>
      </aside>
      <div class="app__body">
        <header class="topbar">
          <h1 class="topbar__title">${esc(document.title)}</h1>
          <span class="topbar__user">${esc(user?.name ?? '')}</span>
          <button class="button" type="button" data-action="sign-out">Sair</button>
        </header>
      </div>`;
    const main = document.querySelector('main');
    main.before(app);
    app.querySelector('.app__body').appendChild(main);
    return true;
  }

  const domReady = () =>
    document.readyState === 'loading'
      ? new Promise((resolve) =>
          document.addEventListener('DOMContentLoaded', resolve, {
            once: true,
          }),
        )
      : Promise.resolve();
  const mounted = domReady()
    .then(mountLayout)
    .catch((error) => {
      showError(error);
      return false;
    });

  /* Every screen with data calls: Mock.ready(async () => { ... }) */
  async function ready(fn) {
    try {
      if ((await mounted) === false) return;
      await fn?.();
    } catch (error) {
      showError(error);
    }
  }

  /* ---------- simulated actions by attribute (no per-screen JS) ----------
     <button data-action="toast" data-message="Salvo (simulado)" data-goto="orders.html">  */
  document.addEventListener('click', (event) => {
    const target = event.target.closest('[data-action]');
    if (!target) return;
    if (target.dataset.action === 'sign-out') signOut();
    if (target.dataset.action === 'toast')
      toast(target.dataset.message || 'Ação simulada', target.dataset.goto);
  });

  return {
    json,
    tables,
    byId,
    param,
    esc,
    currency,
    date,
    badge,
    options,
    toast,
    userId,
    signIn,
    signOut,
    ready,
  };
})();
