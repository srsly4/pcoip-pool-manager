import React from 'react';
import {connect} from 'react-redux';
import Modal from 'react-modal';
import DatePicker from 'react-datepicker';
import moment from 'moment';
import fetch from 'isomorphic-fetch';

import 'react-datepicker/dist/react-datepicker.css';


const customStyles = {
  content: {
    top: '50%',
    left: '50%',
    right: 'auto',
    bottom: 'auto',
    marginRight: '-50%',
    transform: 'translate(-50%, -50%)',
    width: '80vw',
    height: '80vh',
  },
};


class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      poolCount: '',
      modalIsOpen: false,
      startDate: moment(),
      endDate: moment(),
    };

    this.openModal = this.openModal.bind(this);
    this.afterOpenModal = this.afterOpenModal.bind(this);
    this.closeModal = this.closeModal.bind(this);
    this.handleChangeStart = this.handleChangeStart.bind(this);
    this.handleChangeEnd = this.handleChangeEnd.bind(this);
    this.sendRequest = this.sendRequest.bind(this);
    this.setData = this.setData.bind(this);
  }

  setData() {
    this.setState({poolId: this.props.poolId})
  }

  openModal() {
    this.setState({modalIsOpen: true});
  }

  afterOpenModal() {
    // references are now sync'd and can be accessed.
    this.subtitle.style.color = '#000000';
  }

  closeModal() {
    this.setState({modalIsOpen: false});
  }

  onChangeProperty(propertyName, value) {
    const newState = {};
    newState[propertyName] = value;
    this.setState(newState);
  }

  handleChangeStart(date) {
    this.setState({
      startDate: date,
      endDate: date,
    });
  }

  handleChangeEnd(date) {
    this.setState({
      endDate: date,
    });
  }

  sendRequest() {
    fetch(`${this.props.apiUrl}/reservation/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${this.props.token}`,
      },
      body: JSON.stringify({
        pool_id: this.props.poolId,
        slot_count: parseInt(this.state.poolCount, 10),
        start_datetime: this.state.startDate.format('YYYY-MM-DD HH:mm'),
        end_datetime: this.state.endDate.format('YYYY-MM-DD HH:mm'),
      }),
    })
      .then((res) => {
        if (res.status === 409) {
          alert('Could not add reservation');
          return;
        }
        if (res.status !== 201) {
          alert('Error ' + res.status);
          return;
        }
        this.closeModal();
        if (typeof this.props.onSuccessAdd === 'function') {
          this.props.onSuccessAdd();
        }
      })
      .catch(alert);
  }


  render() {
    return (
      <div>
        <button className="button small primary" onClick={ this.openModal }>Reserve</button>
        <Modal
          isOpen={ this.state.modalIsOpen }
          onAfterOpen={ this.afterOpenModal }
          onRequestClose={ this.closeModal }
          style={ customStyles }
          contentLabel="Modal"

        >
          <h4 ref={ subtitle => this.subtitle = subtitle }>{ this.props.name }</h4>
          <div>
            <p>Description:</p>
            <blockquote>{ this.props.info }</blockquote>
          </div>
          <div>
            <label>Slot count:</label>
            <input type="text" id="poolCount" value={ this.state.poolCount } placeholder={ 'max: '+this.props.maxCount}
                   onChange={ event => this.onChangeProperty('poolCount', event.target.value) }
            />
            <label>Reservation start time:</label>
            <DatePicker
              selected={ this.state.startDate }
              onChange={ this.handleChangeStart }
              showTimeSelect
              timeFormat="HH:mm"
              timeIntervals={ 15 }
              dateFormat="LLL"
              timeCaption="time"
            />
            <label>Reservation end time:</label>
            <DatePicker
              selected={ this.state.endDate }
              onChange={ this.handleChangeEnd }
              showTimeSelect
              timeFormat="HH:mm"
              timeIntervals={ 15 }
              dateFormat="LLL"
              timeCaption="time"
            />
          </div>
          <div className="button-group">
            <button className="button primary" onClick={ this.sendRequest }>Rezerwuj</button>
            <button className="button secondary" onClick={ this.closeModal }>Cofnij</button>
          </div>
        </Modal>
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  token: state.user.token,
  apiUrl: state.user.apiUrl,
});

export default connect(mapStateToProps)(App);