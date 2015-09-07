
from django.conf import settings
from django.test import TestCase, override_settings

from unipath import Path

from grunt.forms import NewGameForm
from grunt.models import Game

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
