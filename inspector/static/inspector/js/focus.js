var Message = Backbone.Model.extend({
  urlRoot: 'api/messages'
});

function createPlaybar(message) {
  var svg = d3.select("svg.focus");

  var playerWidth = 300,
      playerHeight = 50;

  svg
    .attr("width", playerWidth)
    .attr("height", playerHeight);

  var timeScale = d3.scale.linear();

  var messageDuration = soundManager.sounds[message.soundId].duration;

  timeScale
    .domain([0, messageDuration])
    .range([0, playerWidth]);

  var timeScrub = d3.svg.brush();

  timeScrub
    .x(timeScale)

  var timeAxis = d3.svg.axis();

  timeAxis
    .tickSize(10)
    .ticks(5)
    .scale(timeScale);

  svgFocus
    .append("g")
    .attr("class", "time axis")
    .attr("transform", "translate(0,10)")
    .call(timeAxis);

  var arc = d3.svg.arc()
    .outerRadius(playerHeight / 2)
    .startAngle(0)
    .endAngle(function(d, i) { return i ? -Math.PI : Math.PI; });

  var brushg = svgFocus.append("g")
    .attr("class", "time brush")
    .call(timeScrub);

  brushg.selectAll(".resize").append("path")
    .attr("transform", "translate(0," +  playerHeight / 2 + ")")
    .attr("d", arc);

  brushg.selectAll("rect")
      .attr("height", playerHeight);

}
