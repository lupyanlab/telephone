
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.models import Message
from inspector.forms import UploadMessageForm

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
