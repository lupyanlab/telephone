from unipath import Path

from django.test import TestCase, override_settings
from django.conf import settings
from django.core.files import File

from model_mommy import mommy

from grunt.models import Game, Chain, Message
from transcribe.forms import NewTranscriptionSurveyForm


class TranscribeModelTest(TestCase):
    def setUp(self):
        super(TranscribeModelTest, self).setUp()
        self.game = mommy.make(Game)


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

        catch_trial_message = Path(settings.APP_DIR,
                                   'transcribe/tests/media/catch_trial.wav')
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
