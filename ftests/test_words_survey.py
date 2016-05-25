from model_mommy import mommy

from words.forms import NewWordSurveyForm
from grunt.models import Message
from ftests.base import FunctionalTest


class WordsTest(FunctionalTest):
    def setUp(self):
        """Populate the DB with some messages to guess the transcriptions of."""
        super(WordsTest, self).setUp()
        mommy.make_recipe('grunt.seed', _quantity=4)


    def test_create_words_survey_from_message_ids(self):
        # Get data required for new word survey form
        choices = Message.objects.values_list('id', flat=True)
        words = ['booba', 'kiki']

        # Navigate to new word survey form
        self.nav_to_word_surveys()
        self.browser.find_element_by_id('id_new_words').click()

        # Fill out new word survey form
        self.fill_form('id_name', 'test new words')
        self.fill_form('id_choices', stringify(choices))
        self.fill_form('id_words', stringify(words))
        self.browser.find_element_by_id('submit-id-submit').click()

        # Land back at the word survey list page
        page_title = self.browser.find_element_by_tag_name('h1').text
        self.assertEquals(page_title, 'Word Surveys')


    def test_take_words_survey(self):
        # Create a word survey
        choices = Message.objects.values_list('id', flat=True)
        words = ['booba', 'kiki']
        data = dict(
            name='ftest',
            num_questions_per_player=2,
            words=stringify(words),
            choices=stringify(choices),
        )
        form = NewWordSurveyForm(data)
        form.save()

        # Navigate to take survey
        self.nav_to_word_surveys()
        self.browser.find_element_by_class_name('take').click()

        # See the first question
        given = self.browser.find_element_by_id('id_word').text
        self.assertIn(given, words)
        words.remove(given)

        # Select a choice
        self.submit_answer()

        # See the second question and answer it
        given = self.browser.find_element_by_id('id_word').text
        self.assertIn(given, words)
        self.submit_answer()

        # Get completion code
        completion_code = self.browser.find_element_by_tag_name('code').text
        parts = completion_code.split('-')
        self.assertEquals(len(parts), 2)


    def test_words_survey_with_catch_trial(self):
        # Create a word survey with a catch trial
        choices = Message.objects.values_list('id', flat=True)
        words = ['booba', 'kiki']
        catch_trial = 'this is the catch trial'
        data = dict(
            name='ftest',
            num_questions_per_player=1,
            words=stringify(words),
            choices=stringify(choices),
            catch_trial='this is the catch trial'
        )
        form = NewWordSurveyForm(data)
        form.save()

        # Navigate to take survey
        self.nav_to_word_surveys()
        self.browser.find_element_by_class_name('take').click()

        # See the catch trial text
        given = self.browser.find_element_by_id('id_word').text
        self.assertEquals(given, catch_trial)


    def nav_to_word_surveys(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_words_list').click()

    def fill_form(self, element_id, text):
        self.browser.find_element_by_id(element_id).send_keys(text)

    def submit_answer(self):
        choices_css = "[type='radio']"
        choices = self.browser.find_elements_by_css_selector(choices_css)
        choices[1].click()
        self.browser.find_element_by_id('submit-id-submit').click()

def stringify(items):
    return ','.join(map(str, items))