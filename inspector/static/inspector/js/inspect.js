function tree(nodes) {
  var nodeById = {};

  // Index the nodes by id, in case they come out of order.
  nodes.forEach(function(d) {
    nodeById[d.id] = d;
  });

  // Lazily compute children.
  nodes.forEach(function(d) {
    if ("manager" in d) {
      var manager = nodeById[d.manager];
      if (manager.children) manager.children.push(d);
      else manager.children = [d];
    }
  });

  return nodes[0];
}

function drawMessageTree(messages) {
  var tree = d3.layout.tree(),
      link = d3.svg.diagonal();

  tree
    .children(function (message) { return message.children; });

  // tree
  //   .size(treeSize)
  //   .children(function (message) { return message.children; });
  //
  // link
  //   .projection(function (message) { return [message.x, message.y + circleSize]; })
  //
  // var svg = d3.select("svg");
  //
  // // Clear the previous chain
  // svg
  //   .selectAll("g")
  //   .remove();
  //
  // svg
  //   .selectAll("path")
  //   .remove();
  //
  // // Adjust the size of the svg element
  // var svgWidth = treeSize[0] + maxTextWidth,
  //     svgHeight = treeSize[1] + circleSize * 2;
  // svg
  //   .attr("width", svgWidth)
  //   .attr("height", svgHeight)
  //
  // // Bind the message data into g elements
  // svg
  //   .selectAll("g.message")
  //   .data(tree(messages))
  //   .enter()
  //   .append("g")
  //   .attr("class", function (message) {
  //     var type = message.audio ? "filled" : "empty";
  //     return "message " + type;
  //   })
  //   .attr("transform", function (message) {
  //     return "translate(0," + circleSize + ")";
  //   });
  //
  // // Add the links
  // svg
  //   .selectAll("path")
  //   .data(tree.links(tree(messages)))
  //   .enter().insert("path","g")
  //   .attr("d", link)
  //   .style("fill", "none")
  //   .style("stroke", "black")
  //   .style("stroke-width", "2px");
  //
  // var messages = svg.selectAll("g.message");
  //
  // // Create a circle for each message
  // messages
  //   .append("circle")
  //   .attr("r", 20)
  //   .attr("cx", function (message) { return message.x; })
  //   .attr("cy", function (message) { return message.y; })

}
