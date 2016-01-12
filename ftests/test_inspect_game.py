from .base import FunctionalTest

class InspectGameTest(FunctionalTest):
    def test_close_chain(self):
        """Marcus decides to close a branch."""
        game_name = 'Dead End Game'
        self.create_game(game_name, nchains=1, depth=1)

        self.nav_to_games_list()
        self.inspect_game(game_name)

        # He selects one of the child nodes.

        # He presses the button to edit it.

        # He changes the number of children to 0.

        # He saves his changes.

        # The node now shows that it is edited, and that it is closed.
