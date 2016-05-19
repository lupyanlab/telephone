from model_mommy import mommy

from grunt.models import Message
from ftests.base import FunctionalTest


class WordsTest(FunctionalTest):
    def setUp(self):
        """Populate the DB with some messages to guess the transcriptions of."""
        super(WordsTest, self).setUp()
        mommy.make_recipe('grunt.seed', _quantity=4)

    def test_create_words_survey_from_message_ids(self):
        # Get data required for new word form
        choices = Message.objects.values_list('id', flat=True)
        words = ['booba', 'kiki']

        # Navigate to new word survey form
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_words_list').click()
        self.browser.find_element_by_id('id_new_words').click()

        # Fill out new word survey form
        self.fill_form('id_name', 'test new words')
        self.fill_form('id_choices', stringify(choices))
        self.fill_form('id_words', stringify(words))
        self.browser.find_element_by_id('submit-id-submit').click()

        # Land back at the word survey list page
        page_title = self.browser.find_element_by_tag_name('h1').text
        self.assertEquals(page_title, 'Word Surveys')

    def fill_form(self, element_id, text):
        self.browser.find_element_by_id(element_id).send_keys(text)


def stringify(items):
    return ','.join(map(str, items))
