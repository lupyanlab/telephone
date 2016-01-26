import Backbone from 'backbone';
import {_} from 'underscore';
import d3 from 'd3';

import {MessageComponent} from 'inspector/js/messages/router.js';


export class GameTreeView extends Backbone.View {

  constructor(options) {
    super(options);
    this.messageComponent = new MessageComponent({el: this.messageDetailsContainerElement});
  }

  get margin() {
    return {top: 20, right: 120, bottom: 20, left: 120};
  }

  get width() {
    return 960 - this.margin.right - this.margin.left;
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
      .size([this.height, this.width])
      .children(node => node.children);

    this.diagonal = d3.svg.diagonal()
      .projection(node => [node.y, node.x]);

    this.svg = d3.selectAll(this.$('svg.tree'))
      .attr("width", this.width + this.margin.right + this.margin.left)
      .attr("height", this.height + this.margin.top + this.margin.bottom)
      .append("g")
      .attr("transform", `translate(${this.margin.left}, ${this.margin.top})`);
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
      .attr("transform", d => `translate(${d.y},${d.x})`);

    nodeEnter.append(addLinkToMessageDetails)
      .append("circle")
      .attr("r", 5)
      .attr("class", d => d.type);

    nodeEnter.append("text")
      .attr("x", -10)
      .attr("dy", ".35em")
      .attr("text-anchor", "end")
      .text(d => d.label);

    let link = this.svg.selectAll("path.link")
      .data(links, d => d.target.nid);

    link.enter().insert("path", "g")
      .attr("class", "link")
      .attr("d", this.diagonal);
  }

  constructGameTreeRootNode() {
    return {
      id: this.model.id,
      type: "game",
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
    let type = "message";
    if (message.isEdited) {
      type = type + " edited"
    }

    return {
      id: message.id,
      type: type,
      label: "#" + message.id,
      children: _.map(message.children, child => this.constructMessageTreeNode(child))
    }
  }

}


function addLinkToMessageDetails(datum) {
  const element = document.createElementNS('http://www.w3.org/2000/svg', 'a');
  if (datum.type === 'message') {
    element.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#messages/${datum.id}/details`); //TODO: Reverse routing
  }
  return element;
}
