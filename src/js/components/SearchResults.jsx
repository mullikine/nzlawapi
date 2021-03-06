"use strict";
var React = require('react/addons');
var Reflux = require('reflux');
var $ = require('jquery');
var Actions = require('../actions/Actions');
var strings = require('../strings');
var SearchTable = require('../mixins/SearchTable.jsx');
var GetMore= require('../mixins/GetMore');


// New definition result based on this
var SearchResult = React.createClass({
    getTitle: function(){
        return (this.props.data.getIn(['fields','title', 0]) || this.props.data.getIn(['fields','full_citation', 0])) || 'Unknown'
    },
    getType: function(){
        return strings.document_types[this.props.data.getIn(['fields','type', 0])];
    },
    getYear: function(){
        return this.props.data.getIn(['fields','year', 0]);
    },
    getContent: function(){
        if(this.props.data.getIn(['highlight','document', 0])){
            var html = (this.props.data.getIn(['highlight','document']) ||[]).join('\u2026');
            return <div dangerouslySetInnerHTML={{__html: html}}/>
        }
    },
    handleLinkClick: function(e){
        e.preventDefault();
        var query = {find: 'full',
            doc_type: this.props.data.getIn(['_type']),
            id: this.props.data.getIn(['fields','id', 0]),
            title: this.props.data.getIn(['fields','title', 0])
        };
        Actions.newPage({query: query, title: this.getTitle()}, this.props.viewer_id);
    },
    render: function(){
        var html = '',
            id = this.props.data.getIn(['fields', 'id', 0]);
        return <tr className="search-result" onClick={this.handleLinkClick}>
        <td>{ this.props.index + 1}</td>
        <td><div><a href={"/open_article/"+this.props.data.get('_type')+'/'+id} >{ this.getTitle() }</a></div>
            { this.getContent() }</td>
        <td> { this.getType() } </td>
        <td> { this.getYear() }</td>
        </tr>
    }
});

module.exports = React.createClass({
    mixins: [
        SearchTable, GetMore
    ],
    propTypes: {
        page: React.PropTypes.object.isRequired
    },
    renderRow: function(data, index){
        return <SearchResult index={index} key={data.getIn(['fields', 'id', 0])+''+index} data={data} viewer_id={this.props.viewer_id}/>;
    },
    render: function(){
        return this.renderTable();
    }
});