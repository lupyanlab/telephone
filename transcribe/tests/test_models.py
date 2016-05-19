import unipath

from django.conf import settings
from django.test import TestCase, override_settings

from model_mommy import mommy

from grunt.models import Message
from transcribe.models import TranscriptionSurvey, MessageToTranscribe, Transcription


TEST_MEDIA_ROOT = unipath.Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TranscriptionTest(TestCase):
    def tearDown(self):
        super(TranscriptionTest, self).tearDown()
        TEST_MEDIA_ROOT.rmtree()

    def test_return_catch_trial(self):
        catch_trial = mommy.make(Message)
        survey = mommy.make_recipe('transcribe.transcription_survey',
            num_transcriptions_per_taker=2)

        messages_to_transcribe = mommy.make_recipe('transcribe.message_to_transcribe', survey=survey, _quantity=20)
        catch_trial_to_transcribe = mommy.make(MessageToTranscribe, survey=survey, given=catch_trial)
        survey.catch_trial_id = catch_trial_to_transcribe.pk
        survey.save()

        transcription = mommy.make(Transcription, message=messages_to_transcribe[0])
        next_message = survey.pick_next_message(receipts=[transcription.pk])
        self.assertEquals(next_message.pk, catch_trial_to_transcribe.pk)
