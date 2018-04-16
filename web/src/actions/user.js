export function didLogin(token) {
  return {
    type: 'LOGIN_FINISHED',
    token,
  };
}

export function didLogout() {
  return {
    type: 'LOGOUT_FINISHED',
  }
}

export default {
  didLogin,
  didLogout,
}