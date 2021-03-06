"use strict";
var React = require('react/addons');
var Input = require('react-bootstrap/lib/Input');
var Button = require('react-bootstrap/lib/Button');
var ButtonToolbar = require('react-bootstrap/lib/ButtonToolbar');
var Actions = require('../actions/Actions');
var PAGE_TYPES = require('../constants').PAGE_TYPES;
var ArticleHandlers = require('./ArticleHandlers.jsx');
var PageMixins = require('../mixins/Page');
var GetMore = require('../mixins/GetMore');
var Popovers = require('./Popovers.jsx');
var PureRenderMixin = require('react/addons').addons.PureRenderMixin;

var DefinitionResult = React.createClass({
    render: function() {
         return (
            <div className="search-result">
                <div dangerouslySetInnerHTML={{__html: this.props.html}}/>
            </div>
        );
    }
});

module.exports = React.createClass({
    mixins: [ArticleHandlers, PageMixins, GetMore, PureRenderMixin],
    propTypes: {
        page: React.PropTypes.object.isRequired
    },
    render: function() {
        var resultContent;

        if(this.props.page.getIn(['content', 'search_results'])) {
            if(this.props.page.getIn(['content', 'search_results', 'hits'])) {
                resultContent = this.props.page.getIn(['content', 'search_results', 'hits']).map(function(r, i) {
                    return r.getIn(['fields', 'html']).map(function(html, j){
                        return <DefinitionResult html={html} key={i+'-'+j}/>
                    })
                });
            }
            else {
                resultContent = <div className="search-count">No Results Found</div>;
            }
        }
        else if(this.props.page.get('fetching')) {
            resultContent = <div className="csspinner" />;
        }
        else {
            resultContent = <div className="article-error"><p className="text-danger">{this.props.page.getIn(['content', 'error'])}</p></div>;
        }
        var total = this.props.page.getIn(['content', 'search_results', 'total']);
        return (
            <div className="search-results legislation-result" onClick={this.interceptLink}>
                <div className="search-count">{total} Results Found</div>
                <Popovers width={this.state.width} viewer_id={this.props.viewer_id} view={this.props.view} page={this.props.page} getScrollContainer={this.getScrollContainer} />

                {resultContent}
            </div>
    );
    }
});
