from .base import FunctionalTest

class CreateSurveyTest(FunctionalTest):
    def setUp(self):
        super(CreateSurveyTest, self).setUp()

    def extract_id_from_message_group(self, message_group):
        svg_text_element = message_group.find_element_by_tag_name('text')
        id_text = svg_text_element.text
        return int(id_text)

    def test_create_survey(self):
        """ Create a new survey using a form """
        # Simulate an ongoing game with 4 chains, each of which has 3 entries
        game_name = 'Game for Ratings'
        nchains = 4
        depth = 3
        self.create_game(game_name, nchains=nchains, with_seed=True,
                         depth=depth)

        # Marcus goes to the home page and sees the ongoing game
        self.browser.get(self.live_server_url)
        self.assertEquals(len(self.select_game_items()), 1)

        # He inspects the game and confirms that the first chain has
        # three entries
        self.inspect_game(game_name)
        message_groups = self.select_svg_messages()
        self.assertEquals(len(message_groups), 1+depth+1)  # seed + filled + empty

        # He notes the id of the first message and the last messages
        # to use in the survey
        messages = []
        choices = []

        messages.append(self.extract_id_from_message_group(message_groups[-2]))
        choices.append(self.extract_id_from_message_group(message_groups[0]))

        # He does the same for the other chains in the game
        for _ in range(nchains-1):
            self.browser.find_element_by_id('id_next_chain').click()
            self.wait_for(tag='body')

            message_groups = self.select_svg_messages()
            messages.append(self.extract_id_from_message_group(message_groups[-2]))
            choices.append(self.extract_id_from_message_group(message_groups[0]))

        # Marcus goes back to the game list page
        self.browser.find_element_by_id('id_game_list').click()

        # Marcus navigates to the survey list page from the home page
        # by clicking the survey list button in the nav bar
        self.browser.find_element_by_id('id_survey_list').click()
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertEquals('Surveys', title)
