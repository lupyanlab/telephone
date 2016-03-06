import Backbone from 'backbone';
import {_} from 'underscore';
import d3 from 'd3';

import {MessageComponent} from 'inspector/js/messages/router.js';


export class GameTreeView extends Backbone.View {

  constructor(options) {
    super(options);
    this.messageComponent = new MessageComponent({el: this.messageDetailsContainerElement});
    this.listenTo(this.messageComponent, 'route:showMessageDetails', this.highlightNode);
  }

  get margin() {
    return {top: 0, right: 10, bottom: 0, left: 10};
  }

  get width() {
    return 1170 - this.margin.right - this.margin.left;
  }

  get height() {
    return 800 - this.margin.top - this.margin.bottom;
  }

  get messageDetailsContainerElement() {
    return this.$('div.message-details');
  }

  render() {
    this.drawMessageTree();
  }

  initialize() {
    this.listenTo(this.model, 'change', this.render);
    this.listenTo(this.model, 'destroy', this.remove);
    this.prepareLayout();
  }

  remove() {
    this.messageComponent.remove();
    super.remove();
  }

  prepareLayout() {
    this.tree = d3.layout.tree()
      .size([this.width, this.height])
      .children(node => node.children);

    this.diagonal = d3.svg.diagonal()
      .projection(node => [node.x, node.y]);

    let x = d3.scale.linear()
      .domain([-this.width/2, this.width/2])
      .range([0, this.width]);

    let y = d3.scale.linear()
      .domain([-this.height/2, this.height/2])
      .range([this.height, 0]);

    let zoom = d3.behavior.zoom()
      .x(x)
      .y(y)
      .scaleExtent([1, 30])
      .on("zoom", this.zoomed);

    this.svg = d3.selectAll(this.$('svg.tree'))
      .attr("width", this.width + this.margin.right + this.margin.left)
      .attr("height", this.height + this.margin.top + this.margin.bottom)
      .append("g")
      .call(zoom)
      .append("g")
      .attr("class", "port");

    this.svg.append("rect")
      .attr("class", "overlay")
      .attr("width", this.width)
      .attr("height", this.height);

    const fontSizeMap = {game: 14, chain: 18, message: 10};
    this.textScale = function(d) {
      return fontSizeMap[d.type];
    }

  }

  zoomed() {
    let svg = d3.select('svg.tree').select('g.port');
    svg.attr("transform", `translate(${d3.event.translate})scale(${d3.event.scale})`);
  }

  drawMessageTree() {
    // Counter for node ids
    let i = 0;

    let nodes = this.tree.nodes(this.constructGameTreeRootNode());
    let links = this.tree.links(nodes);

    nodes.forEach(d => d.y = d.depth * 180);

    let node = this.svg.selectAll("g.node")
      .data(nodes, node => node.nid || (node.nid = ++i));

    let nodeEnter = node.enter()
      .append("g")
      .attr("class", "node")
      .attr("transform", d => `translate(${d.x},${d.y})`);

    let circleSize = 12;

    nodeEnter.append(addLinkToMessageDetails)
      .append("circle")
      .attr("r", circleSize)
      .attr("id", d => `${d.type}-${d.id}`)
      .attr("class", d => d.type)

    // Hide game and chain nodes
    nodeEnter.selectAll("circle.game")
      .attr("opacity", 0.0);
    nodeEnter.selectAll("circle.chain")
      .attr("opacity", 0.0);

    nodeEnter.selectAll("circle.message")
      .attr("class", d => {
        // need to retain "message" as base class
        let class_str = d.type;
        if(d.num_children > 0) {
          class_str += " alive";
        } else if(d.rejected) {
          class_str += " dead";
        } else {
          class_str += " done";
        }
        return class_str;
      });
      //.on("click", d => this.highlightNode(d.id));

    nodeEnter.append("text")
      .attr("x", d => {
        let center = 0, left = -10,
            map = {game: center, chain: left, message: center};
        return map[d.type];
      })
      .attr("y", d => {
        let middle = 0,
            map = {game: middle, chain: middle, message: middle};
        return map[d.type];
      })
      .attr("font-size", d => this.textScale(d.type))
      .attr("dy", ".35em")
      .attr("text-anchor", "middle")
      .attr("pointer-events", d => {
        if(d.type == "message") return "none";
      })
      .text(d => d.label)

    // Add click listener for highlighting nodes
    // nodeEnter.selectAll("circle.message")

    // Add click listener for collapsing nodes to chain objects only
    // nodeEnter.selectAll("circle.")

    let link = this.svg.selectAll("path.link")
      .data(links, d => d.target.nid);

    link.enter().insert("path", "g")
      .attr("class", "link")
      .attr("d", this.diagonal);
  }

  constructGameTreeRootNode() {
    return {
      id: this.model.id,
      type: 'game',
      label: this.model.name,
      children: this.model.chains.map(chain => this.constructChainTreeNode(chain))
    };
  }

  constructChainTreeNode(chain) {
    return {
      id: chain.id,
      label: chain.name,
      type: 'chain',
      children: _.map(chain.seedMessages, seedMessage => this.constructMessageTreeNode(seedMessage))
    }
  }

  constructMessageTreeNode(message) {
    return {
      id: message.id,
      type: 'message',
      rejected: message.rejected,
      label: `#${message.id}`,
      num_children: message.numberOfChildrenLeft,
      children: _.map(message.children, child => this.constructMessageTreeNode(child))
    }
  }

  /**
   * Highlight only the message being detailed in the tree.
   */
  highlightNode(messageId) {
    d3.selectAll("circle.message").classed("highlight", false);
    let node = d3.select(`#message-${messageId}`);
    if(!node.empty()) node.classed("highlight", !node.classed("highlight"));
  }

}


function addLinkToMessageDetails(datum) {
  const element = document.createElementNS('http://www.w3.org/2000/svg', 'a');
  if (datum.type === 'message') {
    element.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#messages/${datum.id}/details`); //TODO: Reverse routing
  }
  return element;
}
