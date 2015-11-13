import Backbone from 'backbone';

import {MessagePlaybarView} from 'inspector/js/messages/crop_message.js';

import messageEditTemplate from 'inspector/js/messages/edit_message.hbs!';
import messageSavedAlertTemplate from 'inspector/js/messages/message_saved_alert.hbs!';


export class MessageEditView extends Backbone.View {

  constructor(options) {
    super(options);
    this.selfTriggeredRender = false;
  }

  get events() {
    return {
      'click .play-button': 'playSound',
      'click .message-save-button': 'saveMessage',
      [`input ${this.numberOfChildrenInputSelector}`]: 'setNumberOfRemainedChildren',
      [`change ${this.editStatusInputSelector}`]: 'setMessageEditStatus',
      [`input ${this.startAtInputSelector}`]: 'setMessageStart',
      [`input ${this.endAtInputSelector}`]: 'setMessageEnd'
    };
  }

  get numberOfChildrenInputSelector() {
    return ':input.message-number-of-children';
  }

  get editStatusInputSelector() {
    return ':input.message-is-edited';
  }

  get startAtInputSelector() {
    return ':input.message-start-at';
  }

  get endAtInputSelector() {
    return ':input.message-end-at';
  }

  get messageSavedAlertLifetime() {
    return 2300;
  }

  get enteredNumberOfChildren() {
    return this.$(this.numberOfChildrenInputSelector).val();
  }

  get editStatus() {
    return this.$(this.editStatusInputSelector).is(':checked');
  }

  get enteredStartAt() {
    return this.$(this.startAtInputSelector).val();
  }

  get enteredEndAt() {
    return this.$(this.endAtInputSelector).val();
  }

  get $messageStatusContainer() {
    return this.$('.message-status');
  }

  get $messageCroppingContainer() {
    return this.$('.message-cropping');
  }

  initialize() {
    this.listenTo(this.model, 'change', this.render);
    this.listenTo(this.model, 'destroy', this.remove);
    this.playbar = new MessagePlaybarView({model: this.model});
  }

  render() {
    if (this.selfTriggeredRender) {
      this.selfTriggeredRender = false;
    } else {
      const html = messageEditTemplate({'message': this.model});
      this.$el.html(html);
      this.$messageCroppingContainer.append(this.playbar.el);
    }
    return this;
  }

  remove() {
    this.undelegateEvents();
    this.stopListening();
    this.playbar.remove();
  }

  setNumberOfRemainedChildren() {
    this.model.set({'num_children': this.enteredNumberOfChildren}, {'silent': true});
  }

  setMessageEditStatus() {
    this.model.set({'edited': this.editStatus}, {'silent': true});
  }

  setMessageStart() {
    this.selfTriggeredRender = true;
    this.model.set({'start_at': this.enteredStartAt});
  }

  setMessageEnd() {
    this.selfTriggeredRender = true;
    this.model.set({'end_at': this.enteredEndAt});
  }

  saveMessage() {
    const response = this.model.save();
    response.done(() => this.flashMessageSavedAlert());
  }

  /** Show alert about saved message for a brief period of time.
   */
  flashMessageSavedAlert() {
    this.showMessageSavedAlert();
    window.setTimeout(() => this.closeMessageAlert(), this.messageSavedAlertLifetime);
  }

  showMessageSavedAlert() {
    const alertHtml = messageSavedAlertTemplate();
    this.$messageStatusContainer.html(alertHtml);
  }

  closeMessageAlert() {
    this.$messageStatusContainer.empty();
  }

  playSound() {
    console.log('Play');
    this.model.sound.play({from: this.model.startAt, to: this.model.endAt});
  }

}
