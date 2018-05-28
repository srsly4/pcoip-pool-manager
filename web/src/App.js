import React, { Component } from 'react';
import {Provider} from 'react-redux';

import store from './store';
import AppRouter from './AppRouter';
import {PersistGate} from 'redux-persist/integration/react';

class App extends Component {
  render() {
    return (
      <Provider store={store.store}>
        <PersistGate loading={null} persistor={store.persistor}>
          <AppRouter/>
        </PersistGate>
      </Provider>
    );
  }
}

export default App;
