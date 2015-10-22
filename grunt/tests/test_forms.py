
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.models import Game
from grunt.forms import ResponseForm, NewChainForm

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


class NewChainFormTest(FormTest):
    def test_create_new_chain_from_form(self):
        game = mommy.make(Game)
        post_data = dict(game=game.pk, name='new chain')
        files_data = dict(seed=self.audio)
        new_chain_form = NewChainForm(post_data, files_data)
        new_chain_form.is_valid()
        print new_chain_form.errors
        self.assertTrue(new_chain_form.is_valid())

    def test_new_chain_form_creates_seed_message(self):
        game = mommy.make(Game)
        post_data = dict(game=game.pk, name='new chain')
        files_data = dict(seed=self.audio)
        new_chain_form = NewChainForm(post_data, files_data)
        new_chain_form.is_valid()
        chain = new_chain_form.save()
        self.assertEquals(chain.messages.count(), 1)
