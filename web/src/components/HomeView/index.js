import React from 'react';
import MainView from '../MainView';
import PoolsView from '../PoolsView'

export default class HomeView extends React.Component {

    render() {
        return (<MainView>
            <PoolsView/>
        </MainView>);
    }
}