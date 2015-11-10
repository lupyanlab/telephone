import Backbone from 'backbone';

import messageDetailsTemplate from 'inspector/js/messages/message_details.hbs!';


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
