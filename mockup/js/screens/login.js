/* Screen: login — picks a user from the users table and stores it in the simulated session. */
Mock.ready(async () => {
  const { users } = await Mock.tables('users');
  const select = document.querySelector('#user');
  Mock.options(select, users);

  document.querySelector('#login-form').addEventListener('submit', (event) => {
    event.preventDefault();
    Mock.signIn(select.value);
    location.href = 'orders.html';
  });
});
