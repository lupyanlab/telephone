
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.forms import ResponseForm

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class FormTest(TestCase):
    def setUp(self):
        super(FormTest, self).setUp()
        self.seed = mommy.make_recipe('grunt.seed')
        test_audio_path = Path(settings.APP_DIR,
                               'grunt/tests/media/test-audio.wav')
        self.audio = File(open(test_audio_path, 'rb'))

    def tearDown(self):
        self.audio.close()
        TEST_MEDIA_ROOT.rmtree()


class ResponseFormTest(FormTest):
    def test_saving_response_form_populates_generation(self):
        response_post = dict(parent=self.seed.id)
        response_files = dict(audio=self.audio)
        response_form = ResponseForm(response_post, response_files)
        message = response_form.save()
        self.assertEquals(message.generation, self.seed.generation + 1)

    def test_saving_response_form_populates_chain(self):
        response_post = dict(parent=self.seed.id)
        response_files = dict(audio=self.audio)
        response_form = ResponseForm(response_post, response_files)
        message = response_form.save()
        self.assertEquals(message.chain, self.seed.chain)
