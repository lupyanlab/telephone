import Backbone from 'backbone';

import messageEditTemplate from 'inspector/js/messages/edit_message.hbs!';
import messageSavedAlertTemplate from 'inspector/js/messages/message_saved_alert.hbs!';


export class MessageEditView extends Backbone.View {

  get events() {
    return {
      'click .play-button': 'playSound',
      'click .message-save-button': 'saveMessage',
      [`input ${this.numberOfChildrenInputSelector}`]: 'setNumberOfRemainedChildren',
      [`change ${this.editStatusInputSelector}`]: 'setMessageEditStatus'
    };
  }

  get numberOfChildrenInputSelector() {
    return ':input.message-number-of-children';
  }

  get editStatusInputSelector() {
    return ':input.message-is-edited';
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

  get $messageStatusContainer() {
    return this.$('.message-status');
  }

  initialize() {
    this.listenTo(this.model, 'change', this.render);
    this.listenTo(this.model, 'destroy', this.remove);
  }

  render() {
    let html = messageEditTemplate({'message': this.model});
    this.$el.html(html);
    return this;
  }

  remove() {
    this.undelegateEvents();
    this.stopListening();
    //this.$el.empty();
  }

  setNumberOfRemainedChildren() {
    this.model.set({'num_children': this.enteredNumberOfChildren}, {'silent': true});
  }

  setMessageEditStatus() {
    this.model.set({'edited': this.editStatus}, {'silent': true});
  }

  saveMessage() {
    const response = this.model.save();
    response.done(() => this.flashMessageSavedAlert());
  }

  /** Show alert about saved message for a brief period of time.
   *
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

}
