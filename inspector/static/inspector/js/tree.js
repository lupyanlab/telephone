import {Messages} from 'inspector/messages.js';


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

}


class Chains extends Backbone.Collection {

  get model() {
    return Chain
  }

}


class Chain extends Backbone.Model {

  // Construct `Chain` from plain Json representation.
  // This method correctly constructs all collections of child models
  // in contrast to the constructor which simply treats them as arrays of plain objects.
  static fromJson(attributes) {
    let updatedAttributes = Chain.prepareJson(attributes);
    return new Chain(updatedAttributes);
  }

  // Ensure that "messages" attribute is a backbone collection of `Message` models,
  // not the array of plain objects.
  static prepareJson(attributes) {
    attributes["messages"] = new Messages(attributes["messages"]);
    return attributes
  }

  // Correctly handles collections of child models.
  parse(response, options) {
    return Chain.prepareJson(response);
  }

}


var margin = {top: 20, right: 120, bottom: 20, left: 120},
    width = 960 - margin.right - margin.left,
    height = 800 - margin.top - margin.bottom;

// Counter for node ids
var i = 0;

var tree = d3.layout.tree()
  .size([height, width])
  .children(function (node) { return node.children; });

var diagonal = d3.svg.diagonal()
  .projection(function (node) { return [node.y, node.x]; });

var svg = d3.select("svg.tree")
  .attr("width", width + margin.right + margin.left)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

function drawMessageTree(nestedData) {
  var nodes = tree.nodes(nestedData),
      links = tree.links(nodes);

  nodes.forEach(function(d) { d.y = d.depth * 180; });

  var node = svg.selectAll("g.node")
    .data(nodes, function(node) { return node.nid || (node.nid = ++i); });

  var nodeEnter = node.enter()
    .append("g")
    .attr("class", "node")
    .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

  nodeEnter.append("circle")
    .attr("r", 5)
    .attr("class", function(d) { return d.type; });

  var messagesWithAudio = nodeEnter.selectAll("circle.message");

  // Load messages with audio using soundManager
  messagesWithAudio.each(function(msg) {
    soundManager.createSound({
      id: msg.soundId,
      url: msg.audio,
      autoload: true
    });
  });

  messagesWithAudio
    .on("click", selectMessage);

  nodeEnter.append("text")
    .attr("x", -10)
    .attr("dy", ".35em")
    .attr("text-anchor", "end")
    .text(function(d) { return d.name || d.generation; });

  var link = svg.selectAll("path.link")
      .data(links, function(d) { return d.target.nid; });

  link.enter().insert("path", "g")
    .attr("class", "link")
    .attr("d", diagonal);
}

function selectMessage(message) {
  console.log(message.id);
}
