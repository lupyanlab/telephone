import unipath
from unittest import skip

from django.test import TestCase, override_settings
from django.conf import settings
from django.core.files import File

from model_mommy import mommy

from grunt.models import Game, Chain, Message
from transcribe.models import MessageToTranscribe
from transcribe.forms import NewTranscriptionSurveyForm, TranscriptionForm

TEST_MEDIA_ROOT = unipath.Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TranscribeFormTest(TestCase):
    def setUp(self):
        super(TranscribeFormTest, self).setUp()
        self.game = mommy.make(Game)

    def tearDown(self):
        super(TranscribeFormTest, self).tearDown()
        TEST_MEDIA_ROOT.rmtree()


    def test_make_new_survey(self):
        survey = NewTranscriptionSurveyForm({
            'name': 'seed generation transcription survey',
            'game': self.game.pk,
            'generation': 0,
            'num_transcriptions_per_taker': 5,
        })
        self.assertTrue(survey.is_valid())


    def test_make_survey_from_message_ids(self):
        chain = mommy.make(Chain, game=self.game)
        mommy.make(Message, chain=chain, _quantity=2)
        message_ids = Message.objects.filter(chain=chain.id).values_list('id', flat=True)

        survey = NewTranscriptionSurveyForm({
            'name': 'make survey from message ids',
            'messages': ','.join(map(str, list(message_ids))),
            'num_transcriptions_per_taker': 5,
        })
        self.assertTrue(survey.is_valid())


    def test_upload_catch_trial_via_form(self):
        chain = mommy.make(Chain, game=self.game)
        mommy.make(Message, chain=chain, _quantity=2)
        message_ids = Message.objects.filter(chain=chain.id).values_list('id', flat=True)

        catch_trial_message = unipath.Path(
            settings.APP_DIR, 'transcribe/tests/media/catch_trial.wav'
        )
        catch_trial = File(open(catch_trial_message, 'rb'))

        post_data = {
            'name': 'make survey from message ids',
            'messages': ','.join(map(str, list(message_ids))),
            'num_transcriptions_per_taker': 5,
        }
        files_data = {'catch_trial': catch_trial}
        survey = NewTranscriptionSurveyForm(post_data, files_data)
        self.assertTrue(survey.is_valid())

        survey = survey.save()
        self.assertEquals(survey.messages.count(), len(message_ids) + 1)


    def test_catch_trial_id_gets_attached_to_survey(self):
        chain = mommy.make(Chain, game=self.game)
        mommy.make(Message, chain=chain, _quantity=2)
        message_ids = Message.objects.filter(chain=chain.id).values_list('id', flat=True)

        catch_trial_message = unipath.Path(
            settings.APP_DIR, 'transcribe/tests/media/catch_trial.wav'
        )
        catch_trial = File(open(catch_trial_message, 'rb'))

        post_data = {
            'name': 'make survey from message ids',
            'messages': ','.join(map(str, list(message_ids))),
            'num_transcriptions_per_taker': 5,
        }
        files_data = {'catch_trial': catch_trial}
        survey = NewTranscriptionSurveyForm(post_data, files_data)
        self.assertTrue(survey.is_valid())

        survey = survey.save()
        self.assertIsNotNone(survey.catch_trial_id)


    @skip("Ignore minimum transcription length for now")
    def test_minimum_transcription_length(self):
        message = mommy.make(MessageToTranscribe)
        form = TranscriptionForm({'message': message.pk, 'text': 'a'})
        self.assertFalse(form.is_valid())
