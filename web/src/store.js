import {applyMiddleware, combineReducers, createStore} from 'redux';
import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage' // defaults to localStorage for web and AsyncStorage for react-native

import thunk from 'redux-thunk';

import reducers from './reducers';

const persistConfig = {
  key: 'root',
  storage,
};

const persistedReducer = persistReducer(persistConfig, combineReducers(reducers));

const store = applyMiddleware(thunk)(createStore)(persistedReducer,
  window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__());
const persistor = persistStore(store);

export default { store, persistor };