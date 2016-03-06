import Backbone from 'backbone';
import {_} from 'underscore';
import d3 from 'd3';


class Playbar {

  constructor(svgElement, scaleDomainSize, selectionStart, selectionEnd) {
    this.svg = svgElement;
    this._scaleDomainSize = scaleDomainSize;
    this._selectionStart = selectionStart;
    this._selectionEnd = selectionEnd;
    this._timeScale = this._makeTimeScale();
    this._timeBrush = this._makeTimeBrush();
  }

  get canvasWidth() {
    return 200;
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

  set onslidermove(listener) {
    const brushMoveCallback = () => listener(...(this._timeBrush.extent()));
    this._timeBrush.on('brush', brushMoveCallback);
  }

  set scaleDomainSize(newScaleDomainSize) {
    this._scaleDomainSize = newScaleDomainSize;
    this._timeScale.domain([0, this._scaleDomainSize]);
  }

  set selectionStart(newSelectionStart) {
    this._selectionStart = newSelectionStart;
    this._resetSelectionArea();
  }

  set selectionEnd(newSelectionEnd) {
    this._selectionEnd = newSelectionEnd;
    this._resetSelectionArea();
  }

  set selectionArea(newSelectionArea) {
    const [selectionStart, selectionEnd] = newSelectionArea;
    this._selectionStart = selectionStart;
    this._selectionEnd = selectionEnd;
    this._resetSelectionArea();
  }

  render() {
    this.svg.attr("width", this.canvasWidth);
    this.svg.attr("height", this.canvasHeight);
    this._drawBorder();
    this._drawControls();
    this._drawTimeAxis();
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

  _drawControls() {
    const scaleRoot = this.svg.append('g');
    scaleRoot.attr("transform", `translate(${this.padding.left}, ${this.padding.top})`);
    this._drawScaleBackground(scaleRoot);
    const brushGroup = this._drawBrush(scaleRoot);
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

  _drawBrush(scaleRoot) {
    const brushGroup = scaleRoot.append("g");
    brushGroup.classed("time brush", true);
    brushGroup.call(this._timeBrush);
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

  _drawTimeAxis() {
    const timeAxis = this._makeTimeAxis();
    const timeAxisGroup = this.svg.append("g");
    timeAxisGroup.classed("time-axis", true);
    timeAxisGroup.attr("transform", `translate(${this.padding.left}, ${this.padding.top})`);
    timeAxisGroup.call(timeAxis);
  }

  _makeTimeBrush() {
    const timeBrush = d3.svg.brush();
    timeBrush.x(this._timeScale);
    timeBrush.extent([this._selectionStart, this._selectionEnd]);
    return timeBrush;
  }

  _makeTimeAxis() {
    const timeAxis = d3.svg.axis();
    timeAxis.innerTickSize(this.contentHeight);
    timeAxis.scale(this._timeScale);
    return timeAxis;
  }

  _makeTimeScale() {
    const timeScale = d3.scale.linear();
    timeScale.domain([0, this._scaleDomainSize]);
    timeScale.range([0, this.contentWidth]);
    return timeScale;
  }

  _resetSelectionArea() {
    this._timeBrush.extent([this._selectionStart, this._selectionEnd]);
  }
}


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

  initialize() {
    this.listenTo(this.model, 'change', this.render);
    this.listenTo(this.model, 'destroy', this.remove);
    const soundDuration = this.model.sound ? this.model.sound.duration: 0; // message sound may be not loaded at this moment
    this.playbar = new Playbar(this.svg, soundDuration, this.model.startAt, this.model.endAt);
    this.playbar.onslidermove = (startAt, endAt) => this.adjustMessageParameters(startAt, endAt);
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
      this.playbar.scaleDomainSize = this.model.sound.duration;
      this.playbar.selectionArea = [this.model.startAt, this.model.endAt];
      this.playbar.render();
    }

    return this;
  }

  adjustMessageParameters(startAt, endAt) {
    this.selfTriggeredRender = true;
    this.model.set({'start_at': startAt, 'end_at': endAt});
  }

}
