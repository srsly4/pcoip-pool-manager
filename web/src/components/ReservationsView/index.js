import React from 'react';
import {connect} from 'react-redux';
import Modal from 'react-modal';
import moment from 'moment';
import fetch from 'isomorphic-fetch';
import ReactTable from "react-table";
import "react-table/react-table.css";
import MainView from '../MainView';
import matchSorter from 'match-sorter';

class ReservationsView extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      reservations: [],
      isAddMultipleReservationsModalOpened: false,
      selectedFile : null,
    }
  }

  componentDidMount() {
    fetch(`${this.props.apiUrl}/reservations?start=${moment().format('YYYY-MM-DD HH:mm:ss')}`, {
      headers: {
        'Authorization': `Token ${this.props.token}`
      }
    })
      .then(resp => resp.json())
      .then(json => {
        this.setState({reservations: json.reservations || []});
      })
      .catch((err) => {
        alert(`Error while getting pools: ${err}`)
      });
  }

  onAddMultipleReservationsClick(e) {
    e.preventDefault();
    if (!this.state.selectedFile) {
      alert('No file selected!');
      return;
    }

    const formData = new FormData();
    formData.append('reservations', this.state.selectedFile, 'reservations');
    const headers = {
      'Accept': 'application/json, */*',
      'Authorization': `Token ${this.props.token}`
    };
    const init = {
      headers,
      method: 'POST',
      body: formData
    };
    fetch(`${this.props.apiUrl}/reservations`, init)
      .then(res => res.text())
      .then(text => alert(text))
      .catch(err => console.error(`An error has occured: ${err}`));
  }

  renderAddMultipleReservationsModal() {
    const customStyles = {
      content : {
        top                   : '50%',
        left                  : '50%',
        right                 : 'auto',
        bottom                : 'auto',
        marginRight           : '-50%',
        transform             : 'translate(-50%, -50%)'
      }
    };
    return (<Modal
      isOpen={this.state.isAddMultipleReservationsModalOpened}
      onRequestClose={() => this.setState({ isAddMultipleReservationsModalOpened: false })}
      contentLabel="Modal"
      style={customStyles}
    >
      <h2>Add multiple reservations</h2>
      <div>
        <label>File to upload:</label>
        <input type="file" id="reservationFiles" onChange={(e) => {
          this.setState({ selectedFile: e.target.files[0] });
        }
        } />
        <button className="button success" onClick={this.onAddMultipleReservationsClick.bind(this)}>Add reservations</button>
      </div>
    </Modal>);
  }

  render() {
    return (
      <MainView>
        <h1>Reservations</h1>
        <div className="button-group">
          <button className="button success" onClick={(e) => {
            e.preventDefault();
            this.setState({ isAddMultipleReservationsModalOpened: true });
          }}>Add multiple reservations</button>
          {this.renderAddMultipleReservationsModal()}
        </div>
        <div>
          <ReactTable
            data={this.state.reservations}
            filterable
            defaultFilterMethod={(filter, row) =>
              String(row[filter.id]) === filter.value}
            columns={[

              {
                Header: "Pool id",
                id:'pool_id',
                accessor: d=>d.pool_id,
                filterMethod: (filter, rows) =>
                  matchSorter(rows, filter.value, { keys: ["pool_id"] }),
                filterAll: true
              },
              {
                Header: "Slots",
                accessor: 'slot_count',
              },
              {
                Header: "Start time",
                id: "start_datetime",
                accessor: d => d.start_datetime,
                filterMethod: (filter, rows) =>
                  matchSorter(rows, filter.value, { keys: ["start_datetime"] }),
                filterAll: true
              },
              {
                Header: "End time",
                id: "end_datetime",
                accessor: d => d.end_datetime,
                filterMethod: (filter, rows) =>
                  matchSorter(rows, filter.value, { keys: ["end_datetime"] }),
                filterAll: true
              },
            ]}
            defaultPageSize={15}
            className="-striped -highlight text-align: center"
          />
        </div>
      </MainView>
    );
  }
}

const mapStateToProps = (state) => ({
  token: state.user.token,
  apiUrl: state.user.apiUrl,
});

export default connect(mapStateToProps)(ReservationsView);