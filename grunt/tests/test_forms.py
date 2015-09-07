import pydub

from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.forms import NewGameForm, TrimMessageForm
from grunt.models import Game, Chain, Message

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


class NewGameFormTest(FormTest):
    def test_make_a_valid_game(self):
        """ Simulate making a new game in the browser """
        form = NewGameForm({'name': 'Valid Game Name', 'num_chains': 1})
        self.assertTrue(form.is_valid())

    def test_valid_form_saves_new_game(self):
        """ Ensure that saving a form creates a new game """
        new_game_name = 'My Real Game'
        form = NewGameForm({'name': new_game_name, 'num_chains': 1})
        form.save()
        last_saved_game = Game.objects.last()
        self.assertEquals(last_saved_game.name, new_game_name)

    def test_new_game_form_saves_with_chain(self):
        """ Ensure that new games are populated with a chain """
        form = NewGameForm({'name': 'New Game', 'num_chains': 1})
        game = form.save()
        self.assertEquals(game.chain_set.count(), 1)

    def test_new_game_form_saves_with_multiple_chains(self):
        """ Should be able to make new games with multiple chains """
        form = NewGameForm({'name': 'Two Chain Game', 'num_chains': 2})
        game = form.save()
        self.assertEquals(game.chain_set.count(), 2)


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
