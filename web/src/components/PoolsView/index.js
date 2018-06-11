import React from 'react';
import {connect} from 'react-redux';

// Import React Table
import ReactTable from "react-table";
import "react-table/react-table.css";
import Modal from '../Modal'
import fetch from "isomorphic-fetch";
import matchSorter from 'match-sorter';
import './index.css';


class PoolsView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: []
        };
    }

    componentDidMount() {
        fetch(`${this.props.apiUrl}/pools/`, {
            headers: {
                'Authorization': `Token ${this.props.token}`
            }
        })
        .then(resp => resp.json())
        .then(resp => {
            this.setState({data: resp});
        })
        .catch((err) => {
            console.log(`Error while getting pools: ${err}`)
        });
    }

    render() {
        const {data} = this.state;
        return (
            <div>
              <h1>Pools</h1>
                <ReactTable
                    data={data}
                    filterable
                    defaultFilterMethod={(filter, row) =>
                        String(row[filter.id]) === filter.value}
                    columns={[

                        {
                            Header: "Name",
                            id:'displayName',
                            accessor: d=>d.displayName,
                            filterMethod: (filter, rows) =>
                                matchSorter(rows, filter.value, { keys: ["displayName"] }),
                            filterAll: true,
                            maxWidth: 300
                        },
                        {
                            Header: "Maximum count",
                            id: "maximumCount",
                            accessor: d => d.maximumCount,
                            maxWidth: 150
                        },
                        {
                            Header: "Description",
                            id: "description",
                            accessor: d => d.description,
                            filterMethod: (filter, rows) =>
                                matchSorter(rows, filter.value, {keys: ["description"]}),
                            filterAll: true,
                        },
                        {
                            Header: 'Actions',
                            id: 'click-me-button',
                            accessor: d=><Modal onSucessAdd={() => { this.componentDidMount(); }}
                                                name={d.displayName} info={d.description} poolId={d.pool_id} maxCount={d.maximumCount}/>,
                            sortable: false,
                            filterable: false,
                            maxWidth: 130
                        },
                    ]}
                    defaultPageSize={15}
                    className="-striped -highlight center"
                />
            </div>
        );
    }
}

const mapStateToProps = (state) => ({
    token: state.user.token,
    apiUrl: state.user.apiUrl,
});

export default connect(mapStateToProps)(PoolsView);
