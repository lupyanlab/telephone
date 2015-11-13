import Backbone from 'backbone';
import {_} from 'underscore';
import d3 from 'd3';


export class MessagePlaybarView extends Backbone.View {

  constructor(options) {
    super(options);
    this.selfTriggeredRender = false;
  }

  get tagName() {
    return "svg";
  }

  get className() {
    return "focus";
  }

  get namespace() {
    return "http://www.w3.org/2000/svg";
  }

  get svg() {
    return d3.select(this.el);
  }

  get canvasWidth() {
    return 660;
  }

  get canvasHeight() {
    return 70;
  }

  get padding() {
    return {top: 17, right: 20, bottom: 17, left: 20};
  }

  get contentWidth() {
    return this.canvasWidth - this.padding.left - this.padding.right;
  }
  get contentHeight() {
    return this.canvasHeight - this.padding.top - this.padding.bottom;
  }

  initialize() {
    this.listenTo(this.model, 'change', this.render);
    this.listenTo(this.model, 'destroy', this.remove);
  }

  /** Overwrite element factory in order to take into account svg namespace.
   *
   * @param tagName
   * @returns {Element}
   * @private
   */
  _createElement(tagName) {
    const namespace = _.result(this, 'namespace');
    return window.document.createElementNS(namespace, tagName);
  }

  render() {

    if (this.selfTriggeredRender) {
      this.selfTriggeredRender = false;
    } else {
      this.$el.empty();

      this.svg.attr("width", this.canvasWidth);
      this.svg.attr("height", this.canvasHeight);

      const timeScale = this._makeTimeScale();
      this._drawBorder();
      this._drawControls(timeScale);
      this._drawTimeAxis(timeScale);
    }

    return this;
  }

  adjustMessageParameters(startAt, endAt) {
    this.selfTriggeredRender = true;
    this.model.set({'start_at': startAt, 'end_at': endAt});
  }

  _drawBorder() {
    const borderCornerRadius = 15;
    const border = this.svg.append('rect');
    border.attr('width', this.canvasWidth);
    border.attr('height', this.canvasHeight);
    border.attr('rx', borderCornerRadius);
    border.attr('ry', borderCornerRadius);
    border.classed('playbar border', true);
  }

  _drawControls(timeScale) {
    const scaleRoot = this.svg.append('g');
    scaleRoot.attr("transform", `translate(${this.padding.left}, ${this.padding.top})`);
    this._drawScaleBackground(scaleRoot);
    const brushGroup = this._drawBrush(scaleRoot, timeScale);
    this._drawSliders(brushGroup);
  }

  _drawScaleBackground(scaleRoot) {
    const scaleBackgroundCornerRadius = 6;
    const scaleBackground = scaleRoot.append('rect');
    scaleBackground.attr('width', this.contentWidth);
    scaleBackground.attr('height', this.contentHeight);
    scaleBackground.attr('rx', scaleBackgroundCornerRadius);
    scaleBackground.attr('ry', scaleBackgroundCornerRadius);
    scaleBackground.classed('playbar scale background', true);
  }

  _drawBrush(scaleRoot, timeScale) {
    const timeBrush = this._makeTimeBrush(timeScale);
    const brushGroup = scaleRoot.append("g");
    brushGroup.classed("time brush", true);
    brushGroup.call(timeBrush);
    brushGroup.selectAll(".time > rect").attr('height', this.contentHeight);
    return brushGroup;
  }

  _drawSliders(brushGroup) {
    const sliderTriangleOffset = 1.5;
    const sliderVerticalBarWidth = 2;

    const upperTriangleSymbol = d3.svg.symbol().type('triangle-down');
    const lowerTriangleSymbol = d3.svg.symbol().type('triangle-up');

    const sliderGroup = brushGroup.selectAll(".resize").append('g').classed('playbar control', true);
    const sliderUpperTriangle = sliderGroup.append('path');
    sliderUpperTriangle.attr("transform", `translate(${sliderTriangleOffset}, 0)`);

    sliderUpperTriangle.attr('d', upperTriangleSymbol);
    const sliderVerticalBar = sliderGroup.append('rect');
    sliderVerticalBar.attr('width', sliderVerticalBarWidth);
    sliderVerticalBar.attr('height', this.contentHeight);

    const sliderLowerTriangle = sliderGroup.append('path');
    sliderLowerTriangle.attr("transform", `translate(${sliderTriangleOffset}, ${this.contentHeight})`);
    sliderLowerTriangle.attr('d', lowerTriangleSymbol);
  }

  _drawTimeAxis(timeScale) {
    const timeAxis = this._makeTimeAxis(timeScale);
    const timeAxisGroup = this.svg.append("g");
    timeAxisGroup.classed("time-axis", true);
    timeAxisGroup.attr("transform", `translate(${this.padding.left}, ${this.padding.top})`);
    timeAxisGroup.call(timeAxis);
  }

  _makeTimeBrush(timeScale) {
    const timeBrush = d3.svg.brush();
    timeBrush.x(timeScale);
    timeBrush.extent([this.model.startAt, this.model.endAt]);
    const brushMoveCallback = () => this.adjustMessageParameters(...(timeBrush.extent()));
    timeBrush.on('brush', brushMoveCallback);
    return timeBrush;
  }

  _makeTimeAxis(timeScale) {
    const timeAxis = d3.svg.axis();
    timeAxis.innerTickSize(this.contentHeight);
    timeAxis.scale(timeScale);
    return timeAxis;
  }

  _makeTimeScale() {
    const messageDuration = this.model.sound.duration;
    const timeScale = d3.scale.linear();
    timeScale.domain([0, messageDuration]);
    timeScale.range([0, this.contentWidth]);
    return timeScale;
  }

}