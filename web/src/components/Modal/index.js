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
        transform: 'translate(-50%, -50%)'
    }
};


class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            poolCount: "",
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

    setData(){
        // console.log(this.props.poolId);
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
            endDate: date
        });
    }

    handleChangeEnd(date) {
        this.setState({
            endDate: date
        });
    }

    sendRequest() {
        fetch(`${this.props.apiUrl}/reservation/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${this.props.token}`
            },
            body: JSON.stringify({
                pool_id: this.props.poolId,
                slot_count: parseInt(this.state.poolCount,10),
                start_datetime: this.state.startDate.format("YYYY-MM-DD HH:mm:ss"),
                end_datetime: this.state.endDate.format("YYYY-MM-DD HH:mm:ss"),
            })
        })
            .then((res) => {
                console.log(this.state.startDate.format());
                if (res.status === 409) {
                    alert('Can\'t add reservation');
                }
                if (res.status !== 201) {
                    alert('Error ' + res.status);
                    return;
                }
                return;
            })
            .then(this.closeModal)
            .catch(alert);
    }



    render() {
        return (
            <div>
                <button className="button small primary" onClick={this.openModal}>Rezerwuj</button>
                <Modal
                    isOpen={this.state.modalIsOpen}
                    onAfterOpen={this.afterOpenModal}
                    onRequestClose={this.closeModal}
                    style={customStyles}
                    contentLabel="Modal"

                >
                    <u><h1 ref={subtitle => this.subtitle = subtitle}>{this.props.name}</h1></u>
                    <div>
                        <br/>
                        <p>Info:</p>
                        <p>{this.props.info}</p>
                    </div>
                    <input type="text" id="poolCount" value={this.state.poolCount} placeholder={"max"}
                           onChange={event => this.onChangeProperty('poolCount', event.target.value)}
                    />
                    <DatePicker
                        selected={this.state.startDate}
                        onChange={this.handleChangeStart}
                        showTimeSelect
                        timeFormat="HH:mm"
                        timeIntervals={15}
                        dateFormat="LLL"
                        timeCaption="time"
                    />
                    <DatePicker
                        selected={this.state.endDate}
                        onChange={this.handleChangeEnd}
                        showTimeSelect
                        timeFormat="HH:mm"
                        timeIntervals={15}
                        dateFormat="LLL"
                        timeCaption="time"
                    />
                    <button onClick={this.sendRequest}>Rezerwuj</button>
                    <button onClick={this.closeModal}>Cofnij</button>
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