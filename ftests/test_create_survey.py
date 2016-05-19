from .base import FunctionalTest

class CreateSurveyTest(FunctionalTest):

    def test_create_survey(self):
        """ Create a new survey using a form """
        # Simulate an ongoing game with 4 chains, each of which has 3 entries
        game_name = 'Game for Ratings'
        nchains = 4
        depth = 3
        self.create_game(game_name, nchains=nchains, depth=depth)

        # Marcus goes to the home page and sees the ongoing game
        self.browser.get(self.live_server_url)
        self.assertEquals(len(self.select_game_items()), 1)

        # He inspects the game and confirms that the first chain has
        # three entries
        self.inspect_game(game_name)
        message_nodes = self.select_message_nodes()
        expected_messages = nchains * (1 + depth)  # seed plus depth generations
        self.assertEquals(len(message_nodes), nchains * (depth + 1))

        # Marcus takes out a piece of paper to note the messages he wants
        # to test
        choices = [extract_id_from_message_node(m) for m in message_nodes[:4]]
        messages = [extract_id_from_message_node(m) for m in message_nodes]

        # Marcus goes back to the game list page
        self.browser.find_element_by_id('id_games_list').click()

        # Marcus navigates to the survey list page from the home page
        # by clicking the survey list button in the nav bar
        self.browser.find_element_by_id('id_survey_list').click()
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertEquals('Surveys', title)

        # He sees that there aren't any surveys in the list yet
        surveys = self.select_survey_items()
        self.assertEquals(len(surveys), 0)

        # He clicks on the New Survey button to create a new survey
        self.browser.find_element_by_id('id_new_survey').click()

        # He fills out the survey form using the messages and choices
        # he jotted down earlier
        survey_name = 'Test Survey'
        messages_str = ','.join(map(str, messages))
        choices_str = ','.join(map(str, choices))
        self.browser.find_element_by_id('id_name').send_keys(survey_name)
        self.browser.find_element_by_id('id_questions').send_keys(messages_str)
        self.browser.find_element_by_id('id_choices').send_keys(choices_str)

        # Then he submits the form
        self.browser.find_element_by_id('submit-id-submit').click()

        # He is redirected back to the survey list page
        # and he sees the new survey on the page
        surveys = self.select_survey_items()
        self.assertEquals(len(surveys), 1)

        # Marcus views the survey by clicking on the view survey button
        survey_item = self.select_survey_item_by_survey_name(survey_name)
        survey_item.find_element_by_class_name('view').click()

        # He sees the name of the survey at the top of the page
        self.assertEquals(self.browser.find_element_by_tag_name('h1').text,
                          survey_name)

        # On the page are as many questions as messages
        question_list = self.browser.find_element_by_id('id_question_list')
        question_items = question_list.find_elements_by_tag_name('li')
        self.assertEquals(len(question_items), len(messages))

def extract_id_from_message_node(message_node):
    """Get the message ids from the svg text element."""
    svg_text_element = message_node.find_element_by_tag_name('text')
    id_text = svg_text_element.text
    return int(id_text)
