/* Screen: orders (list) — joins orders + customers + users + order_statuses.
   Optionally receives ?customer=ID (coming from the customers screen). */
Mock.ready(async () => {
  const { orders, customers, users, order_statuses } = await Mock.tables(
    'orders',
    'customers',
    'users',
    'order_statuses',
  );

  const customerId = Mock.param('customer');
  const statusFilter = document.querySelector('#status-filter');
  Mock.options(statusFilter, order_statuses, 'name', 'Todos os status');

  if (customerId) {
    const notice = document.querySelector('#customer-filter');
    notice.innerHTML = `Mostrando só pedidos de <strong>${Mock.esc(Mock.byId(customers, customerId)?.name)}</strong>. <a href="orders.html">Ver todos</a>`;
    notice.hidden = false;
  }

  function render() {
    const status = Number(statusFilter.value) || null;
    const rows = orders
      .filter((o) => !customerId || o.customer_id === Number(customerId))
      .filter((o) => !status || o.status_id === status)
      .sort((a, b) => b.created_at.localeCompare(a.created_at));

    document.querySelector('#list').innerHTML = rows
      .map(
        (o) => `
      <tr>
        <td><a href="order.html?id=${o.id}">#${o.id}</a></td>
        <td>${Mock.esc(Mock.byId(customers, o.customer_id).name)}</td>
        <td>${Mock.esc(Mock.byId(users, o.assignee_id).name)}</td>
        <td>${Mock.badge(Mock.byId(order_statuses, o.status_id))}</td>
        <td>${Mock.date(o.created_at)}</td>
        <td class="table__num">${Mock.currency(o.amount)}</td>
      </tr>`,
      )
      .join('');
    document.querySelector('#empty').hidden = rows.length > 0;
  }

  statusFilter.addEventListener('change', render);
  render();
});
