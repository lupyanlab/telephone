import Backbone from 'backbone';
import {_} from 'underscore';

import {Message} from 'inspector/js/messages/models.js';


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

  initialize() {
    this.listenTo(this.get('chains'), eventName => this.trigger('change'));
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
    attributes['seedMessages'] = Message.constructMessageHierarchyFromPlainJson(attributes['messages']);
    delete attributes['messages'];
    return attributes
  }

  initialize() {
    // Recursively listen to all of this chain's messages
    let listenToMessage = function (message) {
      _.each(message.get('children'), listenToMessage, this);
      this.listenTo(message, 'change', eventName => this.trigger('change'));
    }
    _.each(this.seedMessages, listenToMessage, this);
  }

  // Correctly handles message hierarchies.
  parse(response, options) {
    return Chain.prepareJson(response);
  }

  get name() {
    return this.get('name');
  }

  get seedMessages() {
    return this.get('seedMessages');
  }

}
