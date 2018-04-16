import {applyMiddleware, combineReducers, createStore} from 'redux';

import thunk from 'redux-thunk';

import reducers from './reducers';

const initialUserState = {
  token: null,
};

const store = applyMiddleware(thunk)(createStore)(combineReducers(reducers));

export default store;