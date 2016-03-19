from django.test import TestCase, override_settings

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
        print survey.errors
        self.assertTrue(survey.is_valid())

    def test_make_survey_from_message_ids(self):
        chain = mommy.make(Chain, game=self.game)
        mommy.make(Message, chain=chain, _quantity=2)
        message_ids = Message.objects.filter(chain=chain.id).values_list('id', flat=True)
        print list(message_ids)
        print map(str, message_ids)
        survey = NewTranscriptionSurveyForm({
            'name': 'make survey from message ids',
            'messages': ','.join(map(str, list(message_ids)))
        })
        print survey.errors
        self.assertTrue(survey.is_valid())
