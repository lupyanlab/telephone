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
      .children(node => node.children)
      .sort((a,b) => a.id - b.id);

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
      .scaleExtent([0, 2])
      .on("zoom", this.zoomed);

    let svg = d3.selectAll(this.$('svg.tree'))
      .attr("width", this.width + this.margin.right + this.margin.left)
      .attr("height", this.height + this.margin.top + this.margin.bottom);

    svg.append("rect")
      .attr("class", "overlay")
      .attr("width", this.width + this.margin.right + this.margin.left)
      .attr("height", this.height + this.margin.top + this.margin.bottom)
      .call(zoom);

    this.svg = svg.append("g");
  }

  zoomed() {
    let svg = d3.select('svg.tree').select('g');
    svg.attr("transform", `translate(${d3.event.translate})scale(${d3.event.scale})`);
  }

  drawMessageTree() {
    let root = this.constructGameTreeRootNode();

    // Calculated width and depth for fixed width tree
    let widthPerNode = 60,
        heightPerGen = 80;
    this.tree.size([widthPerNode * numSiblings, heightPerGen * numGenerations]);

    // Counter for node ids
    let i = 0;

    let nodes = this.tree.nodes(root);
    let links = this.tree.links(nodes);

    nodes.forEach(d => d.y = d.depth * 160);

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

        if(!d.verified) {
          class_str += " unverified";
        }

        if(d.rejected) {
          class_str += " dead";
        } else if(d.num_children > 0) {
          class_str += " alive";
        } else {
          class_str += " done";
        }
        return class_str;
      });

    nodeEnter.append("text")
      .attr("dy", d => {
        if(d.type == "chain") {
          return "-.3em";
        } else {
          return ".35em";
        }
      })
      .attr("text-anchor", "middle")
      .attr("class", d => d.type)
      .attr("pointer-events", d => {
        if(d.type == "message") return "none";
      })
      .text(d => d.label)

    // Add click listener for collapsing nodes to chain objects only
    nodeEnter.selectAll("circle.chain")
      .on("click", function(d) { console.log(d.label); });

    let link = this.svg.selectAll("path.link")
      .data(links, d => d.target.nid);

    link.enter().insert("path", "g")
      .attr("class", d => {
        if(d.source.type == "game") return "link root";
        return "link";
      })
      .attr("d", this.diagonal);

    // Create a map of ancestors
    // Keys are node ids.
    // Items are arrays of message models
    let ancestors = {};

    let saveBranches = function(message) {
      // Add the current message to its ancestry
      let messageAncestors = ancestors[message.id] || [];
      messageAncestors.push(message);
      ancestors[message.id] = messageAncestors

      // Add the current message as the parent of all its children.
      _.each(message.children, child => {
        console.log(child);
        let childAncestors = ancestors[child.id] || [];
        childAncestors.push(message);
        ancestors[child.id] = childAncestors;
        saveBranches(child);
      });
    }

    this.model.chains.forEach(chain => {
      chain.seedMessages.forEach(seed => {
        saveBranches(seed);
      });
    });

    console.log(ancestors);

    link
      .on("mouseover", d => this.highlightBranch(ancestors[d.target.id]))
      .on("click", d => this.playBranch(ancestors[d.target.id]));

    // Hide game label and root links
    d3.selectAll("text.game")
      .attr("opacity", 0.0);
    d3.selectAll("path.root")
      .attr("opacity", 0.0);
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
      verified: message.verified,
      label: `${message.id}`,
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

  /**
   * Highlight the branch of nodes.
   */
  highlightBranch(messageIds) {
    d3.selectAll("circle.message").classed("highlight", false);
    _.each(messageIds, i => {
      d3.select(`#message-${i}`).classed("highlight", true);
    });
  }

  playBranch(messageIds) {
    _.each(messageIds, i => console.log(i));
  }

}


function addLinkToMessageDetails(datum) {
  const element = document.createElementNS('http://www.w3.org/2000/svg', 'a');
  if (datum.type === 'message') {
    element.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#messages/${datum.id}/details`); //TODO: Reverse routing
  }
  return element;
}
