import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base import FunctionalTest

class TakeSurveyTest(FunctionalTest):
    def nav_to_survey_list(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_survey_list').click()

    def test_take_survey(self):
        """ Simulate a person taking a survey """
        # Simulate an ongoing game and a survey created from those messages
        game_name = 'Ongoing Game'
        num_questions = 4
        self.create_game(game_name, nchains=num_questions, depth=3)
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

        # He waits for the message to finish playing
        # and the submit button to become available.
        submit = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.ID, 'submit-id-submit'))
        )

        # Then he listens to the four choices
        # by mousing over the labels

        # He selects the second choice by clicking the radio button
        choices_css = "[type='radio']"
        choices = self.browser.find_elements_by_css_selector(choices_css)
        choices[1].click()

        # Then he clicks submit
        submit.click()

        # He sees an alert message telling him that his submission was
        # successful
        alert = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        alert.click()  # dismiss?

        # He selects choices for the remaining three questions
        num_remaining = num_questions - 1
        for i in range(num_remaining):
            target = self.browser.find_element_by_id('id_target_audio')
            target.click()
            submit = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.ID, 'submit-id-submit'))
            )
            choices = self.browser.find_elements_by_css_selector(choices_css)
            random.choice(choices).click()
            submit.click()

            if i != num_remaining - 1:
                alert = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
                )
                alert.click()  # dismiss?

        # He gets to the completion page
        # His completion code comprises the four pks for his responses,
        # separated by hyphens
        completion_code = self.browser.find_element_by_tag_name('code').text
        parts = completion_code.split('-')
        self.assertEquals(len(parts), num_questions)
