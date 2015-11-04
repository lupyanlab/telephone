import {GameTreeView} from 'inspector/tree.js';
import {GameTree} from 'inspector/tree.js';

class Router extends Backbone.Router {

  get routes() {
    return {
      ':id/inspect(/)': "inspectGame"
    }
  }

  inspectGame(gameId) {
    let game = new GameTree({id: gameId});
    this.view = new GameTreeView({model: game, el: $("svg.tree")});
    game.fetch();
  }

}

class App {

  constructor() {
    this.router = new Router();
    Backbone.history.start({pushState: true});
  }

}

const app = new App();
