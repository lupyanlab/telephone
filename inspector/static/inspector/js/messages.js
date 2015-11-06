import * as Backbone from 'backbone';
import {_} from 'underscore';


export class Message extends Backbone.Model {

  /** Constructs message hierarchy from the plain array.
   *
   * @param {Array<Object>} plainJson plain array, containing JSON representation of the messages
   * @returns {Message} seed message (root of the hierarchy) with correctly set children
   */
  static constructMessageHierarchyFromPlainJson(plainJson) {
    let seedMessageData = _.find(plainJson, messageData => messageData['generation'] === 0);

    let constructMessageSubtree = function(messageData) {
      let childrenMessageData = _.filter(plainJson, m => m['parent'] === messageData['id']);
      messageData['children'] = _.map(childrenMessageData, constructMessageSubtree);
      return new Message(messageData);
    };

    return constructMessageSubtree(seedMessageData);
  }

  get urlRoot() {
    return "inspect/api/messages"
  }

  get soundId() {
    return `s${this.id}`;
  }

  get audio() {
    return this.get('audio');
  }

  get children() {
    return this.get('children');
  }

  get generation() {
    return this.get('generation');
  }

}
