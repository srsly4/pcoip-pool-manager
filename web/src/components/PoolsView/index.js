import React from 'react';

// Import React Table
import ReactTable from "react-table";
import "react-table/react-table.css";
import App from '../Modal'
import fetch from "isomorphic-fetch";
import matchSorter from 'match-sorter'


export default class PoolsView extends React.Component {
    constructor() {
        super();
        this.state = {
            data: []
        };
        this.makeData();
    }

    makeData() {
        return fetch(`http://localhost:8000/pools/`)
            .then(resp => resp.json())
            .then(resp => {
                //console.log(resp['pools'].className);
                this.setState({data: resp['pools']})
                return resp['pools']
            })
    }

    render() {
        const {data} = this.state;
        return (
            <div>
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
                            filterAll: true
                        },
                        {
                            Header: "Maximum count",
                            accessor: 'maximumCount',
                        },
                        {
                            Header: "Description",
                            id: "description",
                            accessor: d => d.description,
                            filterMethod: (filter, rows) =>
                                matchSorter(rows, filter.value, { keys: ["description"] }),
                            filterAll: true

                        },
                        {
                            Header: 'reservation',
                            id: 'click-me-button',
                            accessor: d=><App name={d.displayName} info={d.description}/>

                        },


                    ]}
                    defaultPageSize={15}
                    className="-striped -highlight"
                />
            </div>
        );
    }
}


