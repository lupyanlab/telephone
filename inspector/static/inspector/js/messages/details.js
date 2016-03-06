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

    // should be able to do this in handlebars
    let oneChildLeft = this.model.get("numberOfChildrenLeft") == 1;
    console.log(oneChildLeft);
    let html = messageDetailsTemplate({
      'message': this.model,
      'oneChildLeft': oneChildLeft
    });
    this.$el.html(html);
    return this;
  }

  remove() {
    this.undelegateEvents();
    this.stopListening();
    //this.$el.empty();
  }

  playSound() {
    this.model.sound.play({from: this.model.startAt, to: this.model.endAt});
  }


}
