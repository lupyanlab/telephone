import pydub

from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.models import Message
from inspector.forms import UploadMessageForm, TrimMessageForm

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class FormTest(TestCase):
    def setUp(self):
        super(FormTest, self).setUp()
        self.audio_path = Path(
            settings.APP_DIR,
            'grunt/tests/media/test-audio.wav')

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()


class UploadMessageFormTest(FormTest):
    def setUp(self):
        super(UploadMessageFormTest, self).setUp()
        self.empty_message = mommy.make(Message)

    def test_upload_audio_to_empty_message(self):
        self.assertEqual(self.empty_message.audio, '')

        updated_message = None

        with open(self.audio_path, 'rb') as audio_handle:
            audio_file = File(audio_handle)
            form = UploadMessageForm(instance=self.empty_message,
                                     files={'audio': audio_file})
            self.assertTrue(form.is_valid())

            updated_message = form.save()

        self.assertNotEqual(updated_message.audio, '')


class TrimMessageFormTest(FormTest):
    def setUp(self):
        super(TrimMessageFormTest, self).setUp()
        with open(self.audio_path, 'rb') as audio_handle:
            self.message = mommy.make(Message, audio=File(audio_handle))

    def read_message_audio(self, message):
        return pydub.AudioSegment.from_wav(message.audio.path)

    def test_trim_a_message(self):
        trim_form_data = {
            'message': self.message.id,
            'start': 0.0,
            'end': 1.0,
        }
        trim_form = TrimMessageForm(trim_form_data)
        self.assertTrue(trim_form.is_valid())

        message = trim_form.trim()
        trimmed_segment = self.read_message_audio(message)
        self.assertEquals(trimmed_segment.duration_seconds, 1.0)

    def test_start_comes_before_end(self):
        trim_form_data = {
            'message': self.message.id,
            'start': 1.0,
            'end': 0.0,
        }
        trim_form = TrimMessageForm(trim_form_data)
        self.assertFalse(trim_form.is_valid())
