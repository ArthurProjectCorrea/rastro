/* Screen: customers (list) — shows each customer's order count and links to orders.html?customer=ID. */
Mock.ready(async () => {
  const { customers, orders } = await Mock.tables('customers', 'orders');

  document.querySelector('#list').innerHTML = customers
    .map((c) => {
      const total = orders.filter((o) => o.customer_id === c.id).length;
      return `
      <tr>
        <td>${Mock.esc(c.name)}</td>
        <td>${Mock.esc(c.city)}</td>
        <td>${Mock.esc(c.phone)}</td>
        <td class="table__num"><a href="orders.html?customer=${c.id}">${total}</a></td>
      </tr>`;
    })
    .join('');
});
