import React from 'react';
import {connect} from 'react-redux';
import {Button} from 'react-foundation';
import fetch from 'isomorphic-fetch';

import actions from '../../actions';
import './style.css';

import logo from './logo.jpg';

class LoginView extends React.Component {

  constructor(props) {
    super(props);

    this.doLogin = this.doLogin.bind(this);

    this.state = {
      userLogin: "",
      userPassword: "",
    };

    this.onChangeProperty = this.onChangeProperty.bind(this);
  }

  doLogin(e) {
    e.preventDefault();

    fetch(`${this.props.apiUrl}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: this.state.userLogin,
        password: this.state.userPassword,
      })})
      .then((res) => {
        if (res.status === 404) {
          alert('Incorrect username or password!');
          return;
        }
        this.props.didLogin('not-a-token'); // fixme: use token when delivered by server
      })
      .catch(alert);
  }

  onChangeProperty(propertyName, value) {
    const newState = {};
    newState[propertyName] = value;
    this.setState(newState);
  }

  render() {
    return (
      <div className="login-view-container">
        <div className="login-view callout">
          <img src={logo} alt="PCoIP Pool Manager" />
          <h1>Pool Manager</h1>
          <label htmlFor="userLogin">Login</label>
          <input type="text" id="userLogin" value={this.state.userLogin} placeholder="Login"
            onChange={event => this.onChangeProperty('userLogin', event.target.value)}
          />
          <label htmlFor="userPassword">Hasło</label>
          <input type="password" id="userPassword" value={this.state.userPassword}
            onChange={event => this.onChangeProperty('userPassword', event.target.value)}
          />
          <Button isExpanded color="primary" onClick={this.doLogin}>Zaloguj się</Button>
        </div>
      </div>
    )
  }
}

const mapStateToProps = (state) => ({
  apiUrl: state.user.apiUrl,
});

const mapDispatchToProps = (dispatch) => ({
  didLogin: (token) => dispatch(actions.user.didLogin(token)),
});

export default connect(mapStateToProps, mapDispatchToProps)(LoginView)