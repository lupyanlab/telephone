import unipath
from model_mommy import mommy

from words.forms import NewWordSurveyForm
from grunt.models import Message
from ftests.base import FunctionalTest


class WordsTest(FunctionalTest):
    def setUp(self):
        super(WordsTest, self).setUp()
        # Create the messages to use as choices
        mommy.make_recipe('grunt.seed', _quantity=4)
        self.choices = Message.objects.values_list('id', flat=True)

        # Use the same words in string and file form
        self.words = ['booba', 'kiki']
        self.txt_path = unipath.Path('test-words-upload.txt')
        with open(self.txt_path, 'w') as f:
            for w in self.words:
                f.write(w+'\n')

    def tearDown(self):
        super(WordsTest, self).tearDown()
        # Remove the words file
        if self.txt_path.exists():
            self.txt_path.remove()

    def nav_to_word_surveys(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_words_list').click()


class CreateWordsTest(WordsTest):
    def setUp(self):
        super(CreateWordsTest, self).setUp()
        # Navigate to new word survey form
        self.nav_to_word_surveys()
        self.browser.find_element_by_id('id_new_words').click()

    def fill_form(self, element_id, text):
        self.browser.find_element_by_id(element_id).send_keys(text)

    def test_create_words_survey_from_words_string(self):
        # Fill out new word survey form
        self.fill_form('id_name', 'test new words')
        self.fill_form('id_choices', stringify(self.choices))
        self.fill_form('id_words', stringify(self.words))
        self.browser.find_element_by_id('submit-id-submit').click()

        # Land back at the word survey list page
        page_title = self.browser.find_element_by_tag_name('h1').text
        self.assertEquals(page_title, 'Word Surveys')

    def test_create_words_survey_from_uploaded_csv(self):
        # Fill out new word survey form
        self.fill_form('id_name', 'test new words')
        self.fill_form('id_choices', stringify(self.choices))
        self.fill_form('id_words_file', self.txt_path)
        self.browser.find_element_by_id('submit-id-submit').click()

        # Land back at the word survey list page
        page_title = self.browser.find_element_by_tag_name('h1').text
        self.assertEquals(page_title, 'Word Surveys')


class TakeSurvey(WordsTest):
    def create_word_survey(self, **kwargs):
        form_data = dict(
            name='ftest',
            num_questions_per_player=2,
            words=stringify(self.words),
            choices=stringify(self.choices),
        )
        form_data.update(kwargs)
        form = NewWordSurveyForm(form_data)
        form.save()

    def submit_answer(self):
        choices_css = "[type='radio']"
        choices = self.browser.find_elements_by_css_selector(choices_css)
        choices[1].click()
        self.browser.find_element_by_id('submit-id-submit').click()

    def test_take_words_survey(self):
        self.create_word_survey()

        # Navigate to take survey
        self.nav_to_word_surveys()
        self.browser.find_element_by_class_name('take').click()

        # See the first question
        given = self.browser.find_element_by_id('id_word').text
        self.assertIn(given, self.words)
        self.words.remove(given)

        # Select a choice
        self.submit_answer()

        # See the second question and answer it
        given = self.browser.find_element_by_id('id_word').text
        self.assertIn(given, self.words)
        self.submit_answer()

        # Get completion code
        completion_code = self.browser.find_element_by_tag_name('code').text
        parts = completion_code.split('-')
        self.assertEquals(len(parts), 2)


    def test_take_words_survey_with_catch_trial(self):
        catch_trial = 'this is the catch trial'
        self.create_word_survey(catch_trial=catch_trial,
                                num_questions_per_player=1)

        # Navigate to take survey
        self.nav_to_word_surveys()
        self.browser.find_element_by_class_name('take').click()

        # See the catch trial text
        given = self.browser.find_element_by_id('id_word').text
        self.assertEquals(given, catch_trial)


def stringify(items):
    return ','.join(map(str, items))
