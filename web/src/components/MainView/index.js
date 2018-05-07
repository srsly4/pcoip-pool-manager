import React from 'react';
import actions from '../../actions';
import {connect} from 'react-redux';

import './style.css';

class MainView extends React.Component {
  constructor(props) {
    super(props);

    this.doLogout = this.doLogout.bind(this);
  }

  doLogout(e) {
    e.preventDefault();
    this.props.didLogout();
  }

  render() {
    return (
      <div className="app-container">
        <div className="top-bar">
          <div className="top-bar-left">
            <ul className="menu">
              <li className="menu-text">PCOIP Pool Manager</li>
              <li><a href="#/pools">Pools</a></li>
              <li><a href="#/reservations">Reservations</a></li>
              <li><a href="#/statistics">Statistics</a></li>
            </ul>
          </div>
          <div className="top-bar-right">
            <ul className="menu">
              <li><a href="#" onClick={ this.doLogout }>Logout</a></li>
            </ul>
          </div>
        </div>
        <div className="grid-container">
          <div className="grid-x grid-padding-x">
            <div className="cell small-12 main-view-container">
              { this.props.children }
            </div>
          </div>
        </div>
      </div>);
  }
}

const mapDispatchToProps = (dispatch) => ({
  didLogout: () => dispatch(actions.user.didLogout()),
});

export default connect(null, mapDispatchToProps)(MainView)