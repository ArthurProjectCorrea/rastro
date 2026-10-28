/* Index: lists the screens registered in screens.json. The first screen in the list is the flow entry. */
Mock.ready(async () => {
  const registry = await Mock.json('screens.json');
  document.querySelector('#project').textContent = registry.project;

  const start = document.querySelector('#start');
  if (registry.screens.length) {
    start.href = registry.screens[0].file;
    start.textContent = `Começar por "${registry.screens[0].title}"`;
    start.hidden = false;
  }

  document.querySelector('#screens').innerHTML = registry.screens
    .map(
      (s) => `
    <a class="card card--link" href="${Mock.esc(s.file)}">
      <strong>${Mock.esc(s.title)}</strong>
      <p class="muted">${Mock.esc(s.description ?? '')}</p>
    </a>`,
    )
    .join('');
});
