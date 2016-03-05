import Backbone from 'backbone';
import {_} from 'underscore';


export class Message extends Backbone.Model {

  /** Constructs message hierarchy from the plain array.
   *
   * @param {Array<Object>} plainJson plain array, containing JSON representation of the messages
   * @returns {Message} seed message (root of the hierarchy) with correctly set children
   */
  static constructMessageHierarchyFromPlainJson(plainJson) {
    let seedMessagesData = _.filter(plainJson, messageData => messageData['generation'] === 0);

    let constructMessageSubtree = function(messageData) {
      let childrenMessageData = _.filter(plainJson, m => m['parent'] === messageData['id']);
      messageData['children'] = _.map(childrenMessageData, constructMessageSubtree);
      return new Message(messageData);
    };

    return _.map(seedMessagesData, constructMessageSubtree);
  }

  get urlRoot() {
    return "/inspect/api/messages";
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

  get startAt() {
    return this.get('start_at');
  }

  get endAt() {
    const attributeValue = this.get('end_at');
    if (attributeValue !== null) {
      return attributeValue;
    } else {
      return this.sound.durationEstimate;
    }
  }

  get numberOfChildrenLeft() {
    return this.get('num_children');
  }

  get rejected() {
    return this.get('rejected');
  }

  get generation() {
    return this.get('generation');
  }

  get sound() {
    return soundManager.sounds[this.soundId];
  }

  initialize() {
    this.on('change:id', eventName => this.createSound());
  }

  createSound() {
    const sound = soundManager.createSound({
      id: this.soundId,
      url: this.audio
    });

    sound.load({onload: e => this.trigger('change')}); // Trigger 'change' event to ensure that attached views are rerendered
  }

}
