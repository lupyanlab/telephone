from django.test import TestCase, override_settings

from model_mommy import mommy

from grunt.models import Game
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
