import Backbone from 'backbone';

import {MessageDetailsView} from 'inspector/js/messages/details.js';
import {Message} from 'inspector/js/messages/models.js';


export class MessageComponent extends Backbone.Router {

  constructor(options) {
    super(options);
    this.el = options.el;
    this.messageView = null;
  }

  get routes() {
    return {
      'messages/:id/details(/)': 'showMessageDetails'
    }
  }

  showMessageDetails(messageId) {
    if (this.messageView != null) {
      this.messageView.remove();
    }

    const message = new Message({id: messageId});
    this.messageView = new MessageDetailsView({model: message, el: this.el});
    message.fetch();
  }

}
