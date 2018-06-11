import React from 'react';
import {connect} from 'react-redux';
import moment from 'moment';
import "react-table/react-table.css";
import MainView from '../MainView';
import fetch from 'isomorphic-fetch';
import actions from '../../actions';

class StatisticsView extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      daysShowed: 30,
      statistics: {}
    }
  }

  componentDidMount() {
    this.refreshData();
  }

  refreshData() {
    fetch(`${this.props.apiUrl}/stats?start=${moment().subtract(this.state.daysShowed, 'days').format('YYYY-MM-DD-HH-mm')}`, {
      headers: {
        'Authorization': `Token ${this.props.token}`
      }
    })
      .then(resp => {
        if (resp.status === 401) {
          alert('Unauthenticated');
          this.props.didLogout();
          return null;
        }
        return resp.json();
      })
      .then(resp => {
        console.log(resp);
        this.setState({statistics: resp || {}});
      })
      .catch((err) => {
        console.log(`Error while getting statistics: ${err}`)
      });
  }

  render() {
    return (
      <MainView>
        <h1>Statistics</h1>
        <div className="callout secondary">
          <label>Show statistics for:</label>
          <select value={this.state.daysShowed} onChange={(e) => {
            this.setState({ daysShowed: e.target.value }, () => {
              this.refreshData();
            });
          }}>
            <option value={7}>Week</option>
            <option value={14}>Two weeks</option>
            <option defaultChecked={true} value={30}>Month</option>
          </select>
        </div>
        <div className="grid-x grid-padding-x">
          <div className="small-12 medium-6 cell">
            <div className="callout secondary">
              <h3>Most reserved VMs</h3>
              <table>
                <thead>
                <tr>
                  <th>Pool id</th>
                  <th>Total reserved slots</th>
                </tr>
                </thead>
                <tbody>
                {
                  (this.state.statistics.most_used || []).map((item, index) => {
                    return (<tr key={index}>
                      <td>{item[0] || 'unknown'}</td>
                      <td>{item[1] || 0}</td>
                    </tr>)
                  })
                }
                </tbody>
              </table>
            </div>
          </div>
          <div className="small-12 medium-6 cell">
            <div className="callout secondary">
              <h3>Least reserved VMs</h3>
              <table>
                <thead>
                <tr>
                  <th>Pool id</th>
                  <th>Total reserved slots</th>
                </tr>
                </thead>
                <tbody>
                {
                  (this.state.statistics.least_used || []).map((item, index) => {
                    return (<tr key={index}>
                      <td>{item[0] || 'unknown'}</td>
                      <td>{item[1] || 0}</td>
                    </tr>)
                  })
                }
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </MainView>
    );
  }
}

const mapStateToProps = (state) => ({
  token: state.user.token,
  apiUrl: state.user.apiUrl,
});

const mapDispatchToProps = (dispatch) => ({
  didLogout: () => dispatch(actions.user.didLogout()),
});

export default connect(mapStateToProps, mapDispatchToProps)(StatisticsView);