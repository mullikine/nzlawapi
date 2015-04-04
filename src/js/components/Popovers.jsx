var React = require('react/addons');
var MQ = require('./Responsive.jsx');
var Actions = require('../actions/Actions');
var Popover = require('./Popover.jsx')


var Popovers = React.createClass({
    shouldComponentUpdate: function(newProps){
        return (this.props.popoverView !== newProps.popoverView) || (this.props.popoverData !== newProps.popoverData)
    },
    render: function(){
        return <div>{ this.props.popoverView.map(function(view, key){
                var data = this.props.popoverData.get(key);
                return !data ? null : (<Popover.Popover placement="auto" viewer_id={this.props.viewer_id}
                    popoverPage={data} popoverView={view} page_id={this.props.page_id} id={key} key={key}
                    getScrollContainer={this.props.getScrollContainer}/>)
            }, this).toList()}</div>
    }
 });


var MobilePopovers = React.createClass({
    // Mobile only renders the last one
    shouldComponentUpdate: function(newProps){
        return (this.props.popoverView !== newProps.popoverView) || (this.props.popoverData !== newProps.popoverData)
    },
    closeAll: function(){
        this.props.popoverView.map(function(key){
            Actions.popoverClosed(this.props.viewer_id, this.props.page_id, key);
        }, this),toJS();
    },
    render: function(){
        var last = this.props.popoverView.keys().last();
        if(last !== undefined){
            var pop = this.props.popoverData.get(last);
            return <div className="mobile-popovers">
                    <Popover.MobilePopover popoverPage={pop} page_id={this.props.page_id} closeAll={this.closeAll}/>
                </div>
        }
        return <div/>
    }
});


module.exports = {
    renderFullPopovers: function(props){
        return <MQ minWidth={480}>
            { this.props.view.getIn(['popovers', this.props.page.get('id')]) ?
            <Popovers
                {...props}
                popoverData={this.props.page.get('popovers')}
                popoverView={this.props.view.getIn(['popovers', this.props.page.get('id')])}
                viewer_id={this.props.viewer_id}
                page_id={this.props.page.get('id')} />
            : null }
        </MQ>
    },
    renderMobilePopovers: function(){
        <MQ maxWidth={480}>
            { this.props.view.getIn(['popovers', this.props.page.get('id')]) ?
            <MobilePopovers
                popoverData={this.props.page.get('popovers')}
                popoverView={this.props.view.getIn(['popovers', this.props.page.get('id')])}
                viewer_id={this.props.viewer_id}
                page_id={this.props.page.get('id')} />
            : null }
        </MQ>
    }
};