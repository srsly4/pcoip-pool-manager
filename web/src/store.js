import {applyMiddleware, combineReducers, createStore} from 'redux';

import thunk from 'redux-thunk';

import reducers from './reducers';

const store = applyMiddleware(thunk)(createStore)(combineReducers(reducers));

export default store;