import React from 'react';
import {connect} from 'react-redux';
import {Button} from 'react-foundation';

import actions from '../../actions'
import './style.css'

class LoginView extends React.Component {

  constructor(props) {
    super(props);

    this.doLogin = this.doLogin.bind(this);
  }

  doLogin(e) {
    e.preventDefault();
    alert('Test login!');
    this.props.didLogin('testtoken');
  }

  render() {
    return (
      <div className="login-view-container">
        <div className="login-view callout">
          <label htmlFor="userLogin">Login</label>
          <input type="text" id="userLogin" placeholder="Login" />
          <label htmlFor="userPassword">Hasło</label>
          <input type="password" id="userPassword" />
          <Button color="primary" onClick={this.doLogin}>Zaloguj się</Button>
        </div>
      </div>
    )
  }
}

const mapDispatchToProps = (dispatch) => ({
  didLogin: (token) => dispatch(actions.user.didLogin(token)),
});

export default connect(null, mapDispatchToProps)(LoginView)