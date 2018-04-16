import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Redirect } from 'react-router-dom';
import LoginView from '../LoginView';

class EnsureLoggedInContainer extends Component {

  static propTypes = {
    // From mapStateToProps:
    isLoggedIn: PropTypes.bool.isRequired,
  };

  render() {
    const {
      isLoggedIn,
    } = this.props;

    const location = this.props.location;
    const pathname = location && location.pathname;

    if (!isLoggedIn) {
      switch (pathname) {
        /* put here any other no-login-required paths */
        default:
          return <LoginView {...this.props} />;
      }
    }

    if (this.props.children) {
      return this.props.children;
    }

    return <Redirect to="/" />;
  }
}

const mapStateToProps = (state) => {
  const user = state.user;
  return {
    isLoggedIn: !!(user && user.token),
  };
};

export default connect(mapStateToProps)(EnsureLoggedInContainer);
