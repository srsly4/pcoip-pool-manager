import React from 'react';
import {connect} from 'react-redux';
import "react-table/react-table.css";
import MainView from '../MainView';

class StatisticsView extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      statistics: {
        topReservations: [
          { pool_id: 's7n-girls', total_slots: 17 },
          { pool_id: 's7n-vm1', total_slots: 15 },
          { pool_id: 's7n-vm2', total_slots: 12 },
          { pool_id: 's7n-vm3', total_slots: 5 },
          { pool_id: 's7n-vm4', total_slots: 2 },
        ],
        leastReservations: [
          { pool_id: 's7n-vm11', total_slots: 0 },
          { pool_id: 's7n-vm12', total_slots: 0 },
          { pool_id: 's7n-vm23', total_slots: 0 },
          { pool_id: 's7n-vm34', total_slots: 1 },
          { pool_id: 's7n-vm45', total_slots: 1 },
        ],
      }
    }
  }

  componentDidMount() {
    // fetch(`${this.props.apiUrl}/reservations}`, {
    //   headers: {
    //     'Authorization': `Token ${this.props.token}`
    //   }
    // })
    //   .then(resp => resp.json())
    //   .then(json => {
    //     this.setState({reservations: json.reservations || []});
    //   })
    //   .catch((err) => {
    //     alert(`Error while getting pools: ${err}`)
    //   });
  }

  render() {
    return (
      <MainView>
        <h1>Statistics</h1>
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
                  this.state.statistics.topReservations.map((item, index) => {
                    return (<tr key={index}>
                      <td>{item.pool_id || 'unknown'}</td>
                      <td>{item.total_slots || 0}</td>
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
                  this.state.statistics.leastReservations.map((item, index) => {
                    return (<tr key={index}>
                      <td>{item.pool_id || 'unknown'}</td>
                      <td>{item.total_slots || 0}</td>
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

export default connect(mapStateToProps)(StatisticsView);