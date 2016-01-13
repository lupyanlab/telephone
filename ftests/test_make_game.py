from .base import FunctionalTest

class MakeGameTest(FunctionalTest):
    def fill_out_new_chain_form(self, form_id, chain_name, num_seeds=1):
        chain_name_field = self.browser.find_element_by_id(
            'id_form-{}-name'.format(form_id)
        )
        chain_name_field.send_keys(chain_name)

        for seed_ix in range(num_seeds):
            seed_id = 'id_form-{}-seed{}'.format(form_id, seed_ix)
            seed_field = self.browser.find_element_by_id(seed_id)
            seed_field.send_keys(self.path_to_test_audio())

    def test_make_new_game_via_form(self):
        """Marcus creates a new game using the form."""
        # Marcus navigates to the games list page.
        self.nav_to_games_list()

        # There are no games on the list.
        games_list = self.browser.find_element_by_id('id_game_list')
        games = games_list.find_elements_by_tag_name('li')
        self.assertEqual(len(games), 0)

        # He clicks the new game button to create a new game.
        self.browser.find_element_by_id('id_new_game').click()

        # Marcus fills out the new game form.
        new_game_name = 'My New Game'
        self.browser.find_element_by_id('id_name').send_keys(new_game_name)
        self.browser.find_element_by_id('submit-id-submit').click()

        # After the game is created, he is directed to a page
        # for uploading seeds.

        # He creates a single chain with a seed message. To make
        # a new chain, he needs to provide a name for the chain
        # and the path to the seed message.
        self.fill_out_new_chain_form(form_id=0, chain_name='first chain')
        self.browser.find_element_by_id('submit-id-submit').click()

        # He is redirected to the inspect view for the game
        page_title = self.browser.find_element_by_tag_name('h1').text
        self.assertRegexpMatches(page_title, new_game_name)

        # He returns to the game list page
        self.browser.find_element_by_id('id_games_list').click()

        # He sees his new game on the game list page
        games_list = self.browser.find_element_by_id('id_game_list')
        games = games_list.find_elements_by_tag_name('li')
        self.assertEquals(len(games), 1)
        my_new_game = games[0]
        my_new_game_name = my_new_game.find_element_by_tag_name('h2').text
        self.assertRegexpMatches(my_new_game_name, new_game_name)

    def test_make_game_with_multiple_chains(self):
        """Make a game with multiple chains."""
        self.nav_to_games_list()
        self.browser.find_element_by_id('id_new_game').click()

        new_game_name = 'Two Chain Game'
        num_chains = 2
        self.browser.find_element_by_id('id_name').send_keys(new_game_name)
        # self.browser.find_element_by_id('id_num_chains').send_keys(num_chains)
        self.browser.execute_script(
            'document.getElementById("id_num_chains").setAttribute("value", {});'.format(num_chains)
        )
        self.browser.find_element_by_id('submit-id-submit').click()

        # He fills out two new chain forms
        self.fill_out_new_chain_form(form_id=0, chain_name='first chain')
        self.fill_out_new_chain_form(form_id=1, chain_name='second chain')
        self.browser.find_element_by_id('submit-id-submit').click()

        # He sees the correct number of nodes on the inspect page
        svg_nodes = self.select_svg_nodes()
        # 1 game + 2 chains + 2 seeds
        expected_num_nodes = 1 + 2 + 2
        self.assertEquals(len(svg_nodes), expected_num_nodes)

        # He returns to the game list page
        self.nav_to_games_list()

        # He sees his new game on the game list page
        games_list = self.browser.find_element_by_id('id_game_list')
        games = games_list.find_elements_by_tag_name('li')
        self.assertEquals(len(games), 1)
        my_new_game = games[0]
        my_new_game_name = my_new_game.find_element_by_tag_name('h2').text
        self.assertRegexpMatches(my_new_game_name, new_game_name)

    def test_make_game_with_multiple_seeds_per_chain(self):
        """Marcus makes a game with two seeds in each chain."""
        self.nav_to_games_list()
        self.browser.find_element_by_id('id_new_game').click()

        new_game_name = '2 Chain Game with 2 Seeds Each'
        num_chains = 2
        self.browser.find_element_by_id('id_name').send_keys(new_game_name)
        # self.browser.find_element_by_id('id_num_chains').send_keys(num_chains)
        self.browser.execute_script(
            'document.getElementById("id_num_chains").setAttribute("value", {});'.format(num_chains)
        )

        num_seeds_per_chain = 2
        # self.browser.find_element_by_id('id_num_seeds_per_chain').send_keys(num_chains)
        self.browser.execute_script(
            'document.getElementById("id_num_seeds_per_chain").setAttribute("value", {});'.format(num_seeds_per_chain)
        )
        self.browser.find_element_by_id('submit-id-submit').click()

        # He fills out two new chain forms
        self.fill_out_new_chain_form(form_id=0, chain_name='first chain', num_seeds=2)
        self.fill_out_new_chain_form(form_id=1, chain_name='second chain', num_seeds=2)
        self.browser.find_element_by_id('submit-id-submit').click()

        # He lands on the inspect page and sees the correct number of nodes
        svg_nodes = self.select_svg_nodes()
        # 1 game + 2 chains + 4 seeds (2 seeds per chain)
        expected_num_nodes = 1 + 2 + 4
        self.assertEquals(len(svg_nodes), expected_num_nodes)
