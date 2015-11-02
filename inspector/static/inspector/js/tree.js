import {Message} from 'inspector/messages.js';


export class GameTree extends Backbone.Model {

  static prepareJson(attributes) {
    //Ensure that "chains" attribute is a Backbone collection of `Chain` models instead of array of plain objects.
    // Note: `new Chains(attributes["chains"])` wouldn't work properly because `Chain` attributes also includes
    // array of data that should be converted to Backbone models
    attributes["chains"] = new Chains(_.map(attributes["chains"], chainData => Chain.fromJson(chainData)));
    return attributes
  }

  get urlRoot() {
    return "/inspect/api/games/"
  }

  //Correctly handles collections of child models.
  parse(response, options) {
    return GameTree.prepareJson(response);
  }

  get name() {
    return this.get('name');
  }

  get chains() {
    return this.get('chains');
  }

}


class Chains extends Backbone.Collection {

  get model() {
    return Chain
  }

}


class Chain extends Backbone.Model {

  /** Construct `Chain` from plain Json representation.
   * This method correctly constructs hierarchy of chain messages.
   *
   * @param {Object} attributes - JSON representation of the Chain with messages represented as array
   * @returns {Chain}
   */
  static fromJson(attributes) {
    let updatedAttributes = Chain.prepareJson(attributes);
    return new Chain(updatedAttributes);
  }

  /** Ensure that hierarchy of the chain messages is correctly reconstructed.
   */
  static prepareJson(attributes) {
    attributes['seedMessage'] = Message.constructMessageHierarchyFromPlainJson(attributes['messages']);
    delete attributes['messages'];
    return attributes
  }

  // Correctly handles message hierarchies.
  parse(response, options) {
    return Chain.prepareJson(response);
  }

  get name() {
    return this.get('name');
  }

  get seedMessage() {
    return this.get('seedMessage');
  }

}


export class GameTreeView extends Backbone.View {

  get margin() {
    return {top: 20, right: 120, bottom: 20, left: 120};
  }

  get width() {
    return 960 - this.margin.right - this.margin.left;
  }

  get height() {
    return 800 - this.margin.top - this.margin.bottom;
  }

  render() {
    this.drawMessageTree();
  }

  initialize() {
    this.listenTo(this.model, 'change', this.render);
    this.listenTo(this.model, 'destroy', this.remove);
    this.prepareLayout();
  }

  prepareLayout() {
    this.tree = d3.layout.tree()
      .size([this.height, this.width])
      .children(node => node.children);

    this.diagonal = d3.svg.diagonal()
      .projection(node => [node.y, node.x]);

    this.svg = d3.select(this.el)
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

    nodeEnter.append("circle")
      .attr("r", 5)
      .attr("class", d => d.type);

    let messagesWithAudio = nodeEnter.selectAll("circle.message");

    // Load messages with audio using soundManager
    messagesWithAudio.each(function (msg) {
      soundManager.createSound({
        id: msg.soundId,
        url: msg.audio,
        autoload: true
      });
    });

    messagesWithAudio.on("click", message => console.log(message));

    nodeEnter.append("text")
      .attr("x", -10)
      .attr("dy", ".35em")
      .attr("text-anchor", "end")
      .text(d => d.name || d.generation);

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
      name: this.model.name,
      children: this.model.chains.map(chain => this.constructChainTreeNode(chain))
    };
  }

  constructChainTreeNode(chain) {
    return {
      id: chain.id,
      name: chain.name,
      type: 'chain',
      children: [this.constructMessageTreeNode(chain.seedMessage)]
    }
  }

  constructMessageTreeNode(message) {
    return {
      id: message.id,
      type: 'message',
      soundId: message.soundId,
      audio: message.audio,
      children: _.map(message.children, child => this.constructMessageTreeNode(child))
    }
  }

}
