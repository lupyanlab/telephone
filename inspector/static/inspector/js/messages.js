import Backbone from 'backbone';
import {_} from 'underscore';

import messageDetailsTemplate from 'inspector/js/message_details.hbs!';


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
    return "inspect/api/messages";
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

  get isEdited() {
    return this.get('edited');
  }

  get generation() {
    return this.get('generation');
  }

  get sound() {
    return soundManager.sounds[this.soundId];
  }

}

export class MessageDetailsView extends Backbone.View {

  get events() {
    return {
      'click .play-button': 'playSound'
    };
  }

  initialize() {
    this.listenTo(this.model, 'change', this.render);
    this.listenTo(this.model, 'destroy', this.remove);
  }

  render() {
    let html = messageDetailsTemplate({'message': this.model});
    this.$el.html(html);
    return this;
  }

  remove() {
    this.undelegateEvents();
    this.stopListening();
    //this.$el.empty();
  }

  playSound() {
    this.model.sound.play();
  }


}
