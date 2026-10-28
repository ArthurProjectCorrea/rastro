/* Screen: order-new (form) — fills the selects from the tables; saves nothing. */
Mock.ready(async () => {
  const { customers, users } = await Mock.tables('customers', 'users');

  Mock.options(
    document.querySelector('#customer'),
    customers,
    'name',
    'Selecione um cliente',
  );

  const assignee = document.querySelector('#assignee');
  Mock.options(assignee, users);
  assignee.value = Mock.userId();
});
