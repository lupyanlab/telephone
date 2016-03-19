from model_mommy import mommy

from grunt.models import Game, Chain, Message
from .base import FunctionalTest

class TranscriptionsTest(FunctionalTest):
    def setUp(self):
        """Populate the DB with some messages to transcribe."""
        super(TranscriptionsTest, self).setUp()
        mommy.make_recipe('grunt.seed', _quantity=2)

    def test_create_transcriptions_survey_from_message_ids(self):
        self.assertEquals(Message.objects.count(), 2)
        ids_in_hand = Message.objects.values_list('id', flat=True)
        self.browser.get(self.live_server_url)

        # Navigate to new transcription form.
        self.browser.find_element_by_id('id_transcriptions_list').click()
        self.browser.find_element_by_id('id_new_transcription').click()

        # Fill out the survey form using the messages in hand.
        survey_name = 'Some seed messages'
        messages_str = ','.join(map(str, ids_in_hand))
        self.browser.find_element_by_id('id_name').send_keys(survey_name)
        self.browser.find_element_by_id('id_messages').send_keys(messages_str)
        self.browser.find_element_by_id('submit-id-submit').click()

        # Redirected to transcription survey list view.
        self.assertRegexpMatches(self.browser.current_url,
                                 r'/surveys/transcribe/$')


    def test_create_survey_with_catch_trials(self):
        """Create a transcription survey with catch trials."""
        ids_in_hand = Message.objects.values_list('id', flat=True)
