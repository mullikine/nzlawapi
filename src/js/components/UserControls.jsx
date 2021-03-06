var React = require('react');
var ReportIssue = require('./ReportIssue.jsx');
var Actions = require('../actions/Actions')
var PureRenderMixin = require('react/addons').addons.PureRenderMixin;

module.exports = React.createClass({
    mixins: [PureRenderMixin],
    handleTourStart: function(e){
        e.preventDefault();
        Actions.tourStart();
    },
    render: function(){
        return <div className="user-controls">
            <ReportIssue />
            <a href="#" onClick={this.handleTourStart}>Tour</a>
            { !this.props.loggedIn && <a href={this.props.loginUrl}>Login</a> }
            { this.props.loggedIn && <a href={this.props.accountUrl}>Account</a> }
            { this.props.loggedIn && <a href="/logout">Logout</a> }
        </div>
    },
});