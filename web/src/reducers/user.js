const INITIAL_STATE = {
  data: null,
  token: null,
  apiUrl: 'http://localhost:8000'
};

export default function userReducer(state = INITIAL_STATE, action) {
  switch (action.type) {
    case 'LOGIN_FINISHED':
      return {
        ...state,
        token: action.token,
      };
    case 'LOGOUT_FINISHED':
      return {
        ...state,
        token: null,
      };
    default:
      return state;
  }
}
