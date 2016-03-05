import Backbone from 'backbone';
import {_} from 'underscore';
import d3 from 'd3';

import {MessageComponent} from 'inspector/js/messages/router.js';


export class GameTreeView extends Backbone.View {

  constructor(options) {
    super(options);
    this.messageComponent = new MessageComponent({el: this.messageDetailsContainerElement});
    this.listenTo(this.messageComponent, 'route:showMessageDetails', this.highlightMessage);
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

    let circleSize = 12;

    nodeEnter.append(addLinkToMessageDetails)
      .append("circle")
      .attr("r", circleSize)
      .attr("id", d => `${d.type}-${d.id}`)
      .attr("class", d => d.type)

    nodeEnter.selectAll("circle.message")
      .attr("class", d => {
        // This is probably a terrible idea.
        let class_str = d.type;
        if(d.num_children > 0) {
          class_str += " alive";
        } else if(d.rejected) {
          class_str += " dead";
        } else {
          class_str += " done";
        }
        return class_str;
      })
      .on("click", this.highlightNode);

    nodeEnter.append("text")
      .attr("x", d => {
        let center = 0, left = -10,
            map = {game: center, chain: left, message: center};
        return map[d.type];
      })
      .attr("y", d => {
        let above = -15, middle = 0,
            map = {game: above, chain: middle, message: middle};
        return map[d.type];
      })
      .attr("dy", ".35em")
      .attr("text-anchor", "middle")
      .text(d => d.label);

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
  highlightNode(d) {
    let node = d3.select(`#message-${d.id}`);
    node.classed("highlight", !node.classed("highlight"));
  }

}


function addLinkToMessageDetails(datum) {
  const element = document.createElementNS('http://www.w3.org/2000/svg', 'a');
  if (datum.type === 'message') {
    element.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#messages/${datum.id}/details`); //TODO: Reverse routing
  }
  return element;
}
