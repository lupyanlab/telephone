from .base import FunctionalTest

class InspectGameTest(FunctionalTest):
    def select_message_node(self, svg_circle_element):
        svg_circle_element.find_element_by_xpath("..").click()

    def test_inspect_game(self):
        """Marcus looks at the results of an ongoing game."""
        game_name = 'In Progress Game'
        self.create_game(game_name, nchains=4, depth=4)

        # Marcus goes to the games list and inspects the game
        self.nav_to_games_list()
        self.inspect_game(game_name)

        # He sees the nodes rendered on the svg element
        nodes = self.select_svg_nodes()
        # 1 game node, 4 chain nodes, and each chain has 1 seed and 4 children
        expected_num_nodes = 1 + 4 + (4 * 5)
        self.assertEquals(len(nodes), expected_num_nodes)

    def test_close_chain(self):
        """Marcus decides to close a branch."""
        game_name = 'Dead End Game'
        self.create_game(game_name, nchains=1, depth=1)

        self.nav_to_games_list()
        self.inspect_game(game_name)

        # He selects one of the child nodes.
        nodes = self.select_svg_nodes()
        expected_num_nodes = 1 + 1 + 2
        self.assertEquals(len(nodes), expected_num_nodes)

        message_nodes = self.select_message_nodes()
        self.assertEquals(len(message_nodes), 2)

        seed_message = message_nodes[0]
        self.select_message_node(seed_message)

        # He presses the button to edit it.

        # He changes the number of children to 0.

        # He saves his changes.

        # The node now shows that it is rejected, and that it is closed.
