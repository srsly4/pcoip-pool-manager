import React from 'react';
import Modal from 'react-modal';
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


export default class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            modalIsOpen: false
        };

        this.openModal = this.openModal.bind(this);
        this.afterOpenModal = this.afterOpenModal.bind(this);
        this.closeModal = this.closeModal.bind(this);
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

    render() {
        return (
            <div>
                <button onClick={this.openModal}>Rezerwuj</button>
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

                    <button onClick={this.closeModal}>Rezerwuj</button>
                </Modal>
            </div>
        );
    }
}