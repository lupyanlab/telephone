export class Messages extends Backbone.Collection {

  get urlRoot() {
    return "inspect/api/messages"
  }

  get model() {
    return Message
  }

}


export class Message extends Backbone.Model {

  get soundId() {
    return `s${this.id}`;
  }

}
