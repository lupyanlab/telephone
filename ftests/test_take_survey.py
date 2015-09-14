from .base import FunctionalTest

class TakeSurveyTest(FunctionalTest):
    def nav_to_survey_list(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_survey_list').click()

    def test_take_survey(self):
        """ Simulate a person taking a survey """
        # Simulate an ongoing game and a survey created from those messages
        game_name = 'Ongoing Game'
        self.create_game(game_name, nchains=4, with_seed=True,
                         depth=3)
        survey_name = 'Test Survey'
        survey = self.create_survey(survey_name, from_game=game_name)

        # Martin navigates to the survey via the survey list
        self.nav_to_survey_list()

        # He sees a single survey in the list
        surveys = self.select_survey_items()
        self.assertEquals(len(surveys), 1)

        # He clicks to take the survey
        survey = self.select_survey_item_by_survey_name(survey_name)
        survey.find_element_by_class_name('take').click()

        # First he listens to the target sound
        target = self.browser.find_element_by_id('id_target_audio')
        target.click()

        # Then he listens to the four choices
        # by mousing over the labels

        # He selects the second choice by clicking the radio button
        choices_css = 'input.radio-inline'
        choices = self.browser.find_elements_by_css_selector(choices_css)
        print len(choices_css)
        choices[1].click()

        # He submits the survey
        self.browser.find_element_by_id('submit-id-submit').click()
