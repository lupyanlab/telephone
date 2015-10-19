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
    .attr("r", 5);

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
