var React = require('react/addons');
var Modal = require('react-bootstrap/lib/Modal');
var Graph = require('./Graph.jsx');

module.exports =  React.createClass({
    render: function() {
        return (
            <Modal {...this.props} title="Act Reference Map" className={'graph-modal'} animation={false}>
                <div className="modal-body">
                    <Graph />
                </div>
            </Modal>
        );
    }
});
