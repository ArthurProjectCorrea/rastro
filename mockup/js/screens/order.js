/* Screen: order (detail) — receives ?id=ID and shows the order with customer, assignee and status. */
Mock.ready(async () => {
  const { orders, customers, users, order_statuses } = await Mock.tables(
    'orders',
    'customers',
    'users',
    'order_statuses',
  );

  const order = Mock.byId(orders, Mock.param('id'));
  if (!order) {
    document.querySelector('#not-found').hidden = false;
    return;
  }
  const customer = Mock.byId(customers, order.customer_id);

  document.querySelector('#number').textContent = `#${order.id}`;
  document.querySelector('#order-detail').innerHTML = `
    <dt>Status</dt><dd>${Mock.badge(Mock.byId(order_statuses, order.status_id))}</dd>
    <dt>Responsável</dt><dd>${Mock.esc(Mock.byId(users, order.assignee_id).name)}</dd>
    <dt>Criado em</dt><dd>${Mock.date(order.created_at)}</dd>
    <dt>Valor</dt><dd>${Mock.currency(order.amount)}</dd>
    <dt>Descrição</dt><dd>${Mock.esc(order.description ?? 'Sem descrição')}</dd>`;
  document.querySelector('#customer-detail').innerHTML = `
    <dt>Nome</dt><dd>${Mock.esc(customer.name)}</dd>
    <dt>Cidade</dt><dd>${Mock.esc(customer.city)}</dd>
    <dt>Telefone</dt><dd>${Mock.esc(customer.phone)}</dd>`;
  document.querySelector('#customer-orders').href =
    `orders.html?customer=${customer.id}`;

  document.querySelector('#order-content').hidden = false;
  document.querySelector('#actions').hidden = false;
});
