import React from 'react';
import {HashRouter} from 'react-router-dom';
import EnsureLoggedInPath from './components/EnsureLoggedInPath';
import HomeView from './components/HomeView';
import ReservationsView from './components/ReservationsView';

export default class AppRouter extends React.Component {
  render() {
      return (<HashRouter>
        <div>
          <EnsureLoggedInPath exact path="/" component={HomeView} />
          <EnsureLoggedInPath exact path="/pools" component={HomeView} />
          <EnsureLoggedInPath exact path="/reservations" component={ReservationsView} />
        </div>
      </HashRouter>);
  }
}