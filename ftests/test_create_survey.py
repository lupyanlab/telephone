from .base import FunctionalTest

class CreateSurveyTest(FunctionalTest):
    def setUp(self):
        super(CreateSurveyTest, self).setUp()

    def extract_id_from_message_group(self, message_group):
        """ Get the message ids from the svg text element """
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

        # Marcus takes out a piece of paper to note the messages he wants
        # to test
        messages = []
        choices = []

        # He notes the id of the first message and the last messages
        # to use in the survey
        messages.append(self.extract_id_from_message_group(message_groups[-2]))
        choices.append(self.extract_id_from_message_group(message_groups[0]))

        # He does the same for the other chains in the game
        remaining_chains = nchains - 1
        for _ in range(remaining_chains):
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

        # He sees that there aren't any surveys in the list yet
        survey_list = self.browser.find_element_by_id('id_survey_list')
        surveys = survey_list.find_elements_by_tag_name('li')
        self.assertEquals(len(surveys), 0)

        # He clicks on the New Survey button to create a new survey
        self.browser.find_element_by_id('id_new_survey').click()
        self.wait_for(tag='body')

        # He fills out the survey form using the messages and choices
        # he jotted down earlier
        messages_str = ','.join(messages)
        choices_str = ','.join(choices)
        self.browser.find_element_by_id('id_questions').send_keys(message_str)
        self.browser.find_element_by_id('id_choices').send_keys(choices_str)

        # Then he submits the form
        self.browser.find_element_by_id('submit-id-submit').click()

        # He is redirected back to the survey list page
        # and he sees the new survey on the page
        survey_list = self.browser.find_element_by_id('id_survey_list')
        surveys = survey_list.find_elements_by_tag_name('li')
        self.assertEquals(len(surveys), 1)