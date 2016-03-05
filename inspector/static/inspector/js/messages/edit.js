import Backbone from 'backbone';

import {MessagePlaybarView} from 'inspector/js/messages/crop_message.js';

import messageEditTemplate from 'inspector/js/messages/edit_message.hbs!';
import messageSavedAlertTemplate from 'inspector/js/messages/message_saved_alert.hbs!';
import messageSaveErrorAlertTemplate from 'inspector/js/messages/message_save_error_alert.hbs!';


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
    return ':input.message-is-rejected';
  }

  get startAtInputSelector() {
    return ':input.message-start-at';
  }

  get endAtInputSelector() {
    return ':input.message-end-at';
  }

  get messageStatusAlertLifetime() {
    return 5300;
  }

  get $startAtInput() {
    return this.$(this.startAtInputSelector);
  }

  get $endAtInput() {
    return this.$(this.endAtInputSelector);
  }

  get enteredNumberOfChildren() {
    return this.$(this.numberOfChildrenInputSelector).val();
  }

  get editStatus() {
    return this.$(this.editStatusInputSelector).is(':checked');
  }

  get enteredStartAt() {
    return this.$startAtInput.val();
  }

  set enteredStartAt(newStartAt) {
    this.$startAtInput.val(newStartAt);
  }

  get enteredEndAt() {
    return this.$endAtInput.val();
  }

  set enteredEndAt(newEndAt) {
    this.$endAtInput.val(newEndAt);
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
      this.previousEnteredStartAt = this.enteredStartAt;
      this.previousEnteredEndAt = this.enteredEndAt;
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
    this.model.set({'rejected': this.editStatus}, {'silent': true});
  }

  setMessageStart() { // TODO: Model-side validation
    if ((this.enteredStartAt >= 0) && (this.enteredStartAt <= this.model.endAt)) { // Do not set model `start_at` to invalid value
      this.selfTriggeredRender = true;
      this.model.set({'start_at': this.enteredStartAt});
      this.previousEnteredStartAt = this.enteredStartAt;
    } else {
      this.enteredStartAt = this.previousEnteredStartAt; // Set UI to previous correct value
    }
  }

  setMessageEnd() {// TODO: Model-side validation
    if ((this.enteredEndAt <= this.model.sound.durationEstimate) && (this.enteredEndAt >= this.model.startAt)) { // Do not set model `end_at` attribute to invalid value
      this.selfTriggeredRender = true;
      this.model.set({'end_at': this.enteredEndAt});
      this.previousEnteredEndAt = this.enteredEndAt;
    } else {
      this.enteredEndAt = this.previousEnteredEndAt; // Set UI to previous correct value
    }
  }

  saveMessage() {
    const response = this.model.save();
    response.done(() => this.flashMessageSavedAlert());
    response.fail(() => this.flashMessageSaveErrorAlert());
  }

  /** Show alert about error with message saving for a brief period of time.
   *
   */
  flashMessageSaveErrorAlert() {
    this.showMessageSaveErrorAlert();
    this.scheduleMessageStatusAlertRemoval();
  }

  /** Show alert about saved message for a brief period of time.
   */
  flashMessageSavedAlert() {
    this.showMessageSavedAlert();
    this.scheduleMessageStatusAlertRemoval();
  }

  /** Remove alert about message status after a brief amount of time.
   */
  scheduleMessageStatusAlertRemoval() {
    window.setTimeout(() => this.closeMessageAlert(), this.messageStatusAlertLifetime);
  }

  showMessageSavedAlert() {
    this.showMessageStatusAlert(messageSavedAlertTemplate);
  }

  showMessageSaveErrorAlert() {
    this.showMessageStatusAlert(messageSaveErrorAlertTemplate);
  }

  showMessageStatusAlert(template) {
    const alertHtml = template();
    this.$messageStatusContainer.html(alertHtml);
  }

  closeMessageAlert() {
    this.$messageStatusContainer.empty();
  }

  playSound() {
    this.model.sound.play({from: this.model.startAt, to: this.model.endAt});
  }

}
