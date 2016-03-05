
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.models import Game, Chain, Message

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ModelTest(TestCase):
    def tearDown(self):
        """Remove the test media root."""
        TEST_MEDIA_ROOT.rmtree()


class GameTest(ModelTest):
    def test_make_a_game(self):
        """Make a game."""
        game = Game(name='New Game')
        game.full_clean()
        game.save()

    def test_get_messages_by_generation(self):
        """Select messages from a game by generation."""
        game = mommy.make(Game)
        chains = mommy.make(Chain, game=game, _quantity=2)
        expected = []
        for chain in chains:
            first = mommy.make(Message, chain=chain)
            second = mommy.make(Message, chain=chain, parent=first, generation=1)
            expected.append(first)

        actual = game.get_messages_by_generation(0)
        for e, a in zip(expected, actual):
            self.assertEquals(e, a)


class ChainTest(ModelTest):
    def setUp(self):
        super(ChainTest, self).setUp()
        self.game = mommy.make(Game)

    def test_make_a_chain(self):
        """Make a chain."""
        chain = Chain(game=self.game, name='New Chain')
        chain.full_clean()
        chain.save()

    def test_pick_youngest_parent(self):
        """Chains should pick the youngest parent message.

        This is not a good test because it won't always fail even if
        the picking isn't implemented correctly!
        """
        chain = mommy.make(Chain)
        young = mommy.make(Message, chain=chain)
        old = mommy.make(Message, chain=chain, generation=1)
        parent = chain.pick_parent()
        self.assertEquals(parent, young)


class MessageTest(ModelTest):
    def setUp(self):
        super(MessageTest, self).setUp()
        self.chain = mommy.make(Chain)

        # test file for models.FileField
        fpath = Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')
        self.audio = File(open(fpath, 'rb'))

    def tearDown(self):
        super(MessageTest, self).tearDown()
        self.audio.close()

    def test_make_a_seed_message(self):
        """Make a seed message: a message without a parent."""
        message = Message(chain=self.chain, audio=self.audio)
        message.full_clean()
        message.save()

    def test_make_a_response_message(self):
        """Make a message."""
        seed = mommy.make_recipe('grunt.seed')
        message = Message(parent=seed, audio=self.audio)
        message.full_clean()
        message.save()
        self.assertEquals(message.parent, seed)
