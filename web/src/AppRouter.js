import React from 'react';
import {HashRouter} from 'react-router-dom';
import EnsureLoggedInPath from './components/EnsureLoggedInPath';
import HomeView from './components/HomeView';

export default class AppRouter extends React.Component {
  render() {
      return (<HashRouter>
        <div>
          <EnsureLoggedInPath exact path="/" component={HomeView} />
          <EnsureLoggedInPath exact path="/pools" component={HomeView} />
        </div>
      </HashRouter>);
  }
}