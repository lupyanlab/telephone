import Backbone from 'backbone';

import {GameTreeView} from 'inspector/js/tree.js';
import {GameTree} from 'inspector/js/tree.js';

class Router extends Backbone.Router {

  get routes() {
    return {
      ':id/inspect(/)': "inspectGame"
    }
  }

  inspectGame(gameId) {
    const game = new GameTree({id: gameId});
    this.view = new GameTreeView({model: game, el: "div.game-tree"});
    game.fetch();
    Backbone.history.stop(); // Stop the router that uses standard URLs and run hash fragment-based one
    Backbone.history.start({pushState: false});
  }

}

class App {

  constructor() {
    this.router = new Router();
    Backbone.history.start({pushState: true}); // Run router that uses standard URLs. TODO: May not work in old browsers
  }

}

const app = new App();
