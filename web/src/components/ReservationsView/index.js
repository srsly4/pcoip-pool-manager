import React from 'react';
import {connect} from 'react-redux';
import Modal from 'react-modal';
import fetch from 'isomorphic-fetch';
import MainView from '../MainView';

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
    fetch(`${this.props.apiUrl}/reservations/`, {
      headers: {
        'Authorization': `Token ${this.props.token}`
      }
    })
      .then(resp => resp.json())
      .then(json => {
        this.setState({reservations: json.reservations || []});
      })
      .catch((err) => {
        console.log(`Error while getting pools: ${err}`)
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
    fetch(`${this.props.apiUrl}/reservations/`, init)
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
    console.log(this.state.reservations);
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
          <table>
            <thead>
            <tr>
              <th>Pool</th>
              <th>Slots</th>
              <th>User</th>
              <th>Date and time</th>
              <th>Actions</th>
            </tr>
            </thead>
            <tbody>
            { this.state.reservations.map((reservation) => {
              return (<tr>
                <td>{(reservation.pool || {}).displayName}</td>
                <td>{reservation.slots}</td>
                <td></td>
                <td></td>
                <td><button className="button danger small">Remove</button></td>
              </tr>)
            }) }
            </tbody>
          </table>
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