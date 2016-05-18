from unipath import Path

from model_mommy import mommy

from grunt.models import Game, Chain, Message
from transcribe.forms import NewTranscriptionSurveyForm
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

        self.navigate_to_new_transcription_form()

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
        """Create a transcription survey with a catch trial."""
        ids_in_hand = Message.objects.values_list('id', flat=True)
        catch_audio = Path('transcribe/tests/media/catch_trial.wav').absolute()
        self.browser.get(self.live_server_url)

        self.navigate_to_new_transcription_form()

        # Fill out the survey form and upload the catch trial.
        survey_name = 'Survey with a catch trial'
        messages_str = ','.join(map(str, ids_in_hand))
        self.browser.find_element_by_id('id_name').send_keys(survey_name)
        self.browser.find_element_by_id('id_messages').send_keys(messages_str)
        self.browser.find_element_by_id('id_catch_trial').send_keys(catch_audio)
        self.browser.find_element_by_id('submit-id-submit').click()

        # Redirected to transcription survey list view.
        self.assertRegexpMatches(self.browser.current_url,
                                 r'/surveys/transcribe/$')


    def test_take_transcription_survey(self):
        """Transcribe a single message.

        Requires a transcription survey to be made.
        """
        survey_name = 'test take a transcription survey'
        ids_in_hand = Message.objects.values_list('id', flat=True)
        form = NewTranscriptionSurveyForm({
            'name': survey_name,
            'messages': ','.join(map(str, ids_in_hand)),
            'num_transcriptions_per_taker': 2,
        })
        form.save()

        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_transcriptions_list').click()


    def navigate_to_new_transcription_form(self):
        self.browser.find_element_by_id('id_transcriptions_list').click()
        self.browser.find_element_by_id('id_new_transcription').click()
