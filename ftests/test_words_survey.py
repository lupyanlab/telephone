from model_mommy import mommy

from grunt.models import Message
from ftests.base import FunctionalTest


class WordsTest(FunctionalTest):
    def setUp(self):
        """Populate the DB with some messages to guess the transcriptions of."""
        super(WordsTest, self).setUp()
        mommy.make_recipe('grunt.seed', _quantity=4)

    def test_create_words_survey_from_message_ids(self):
        self.assertEquals(Message.objects.count(), 4)

        # data for form
        name = 'test new words'
        ids_in_hand = Message.objects.values_list('id', flat=True)
        choices_str = ','.join(map(str, ids_in_hand))
        word_list = 'booba,kiki'

        # navigate to new word survey form
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_words_list').click()
        self.browser.find_element_by_id('id_new_words').click()

        self.fail()
