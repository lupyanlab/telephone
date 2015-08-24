import json

from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from unipath import Path
from model_mommy import mommy

from grunt.models import Game, Chain, Message

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class ViewTest(TestCase):
    def setUp(self):
        self.audio_path = Path(
            settings.APP_DIR,
            'grunt/tests/media/test-audio.wav')

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()

    def make_session(self, game, instructed = False, receipts = list(),
                     messages = list()):
        self.client.get(game.get_absolute_url())
        session = self.client.session
        session['instructed'] = instructed
        session['receipts'] = receipts
        session['messages'] = messages
        session.save()


class InspectViewTest(ViewTest):
    def test_game_inspect_url(self):
        """ Games should return a url for viewing the clusters """
        game = mommy.make(Game)
        expected_url = reverse('inspect', kwargs = {'pk': game.pk})
        self.assertEquals(expected_url, game.get_inspect_url())

    def test_inspect_template(self):
        """ Inspecting a game uses the inspect.html template """
        game = mommy.make(Game)
        response = self.client.get(game.get_inspect_url())
        self.assertTemplateUsed(response, 'inspector/inspect.html')


class UploadMessageViewTest(ViewTest):
    def test_uploading_audio_to_empty_message_fills_that_message(self):
        empty_message = mommy.make(Message)

        self.assertEquals(empty_message.audio, '')

        url = reverse('upload', kwargs = {'pk': empty_message.pk})
        with open(self.audio_path, 'rb') as audio_handle:
            self.client.post(url, {'audio': audio_handle})

        seed_message = Message.objects.get(pk = empty_message.pk)
        self.assertNotEqual(seed_message.audio, '')

    def test_uploading_audio_to_empty_message_sprouts_new_message(self):
        chain = mommy.make(Chain)
        seed_message = mommy.make(Message, chain = chain)
        url = reverse('upload', kwargs = {'pk': seed_message.pk})
        with open(self.audio_path, 'rb') as audio_handle:
            self.client.post(url, {'audio': audio_handle})

        messages_in_chain = chain.message_set.all()
        self.assertEquals(len(messages_in_chain), 2)

        last_message = chain.message_set.last()
        self.assertEquals(last_message.parent, seed_message)


class CloseViewTest(ViewTest):
    def test_close_message_chain(self):
        chain = mommy.make(Chain)
        seed = mommy.make(Message, chain = chain)
        child = mommy.make(Message, parent = seed, chain = chain)

        seed_children = seed.message_set.all()
        self.assertEquals(len(seed_children), 1)

        url = reverse('close', kwargs = {'pk': child.pk})
        self.client.post(url)

        chain_messages = chain.message_set.all()
        self.assertEquals(len(chain_messages), 1)

        seed_children = seed.message_set.all()
        self.assertEquals(len(seed_children), 0)
