import React from 'react';
import {HashRouter} from 'react-router-dom';
import Foundation from 'react-foundation';
import EnsureLoggedInPath from './components/EnsureLoggedInPath';
import HomeView from './components/HomeView';

export default class AppRouter extends React.Component {
  render() {
      return (<HashRouter>
        <EnsureLoggedInPath exact path="/" component={HomeView} />
      </HashRouter>);
  }
}