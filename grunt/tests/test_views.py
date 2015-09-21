import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from unipath import Path
from model_mommy import mommy

from grunt.models import Game, Chain, Message

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ViewTest(TestCase):
    def setUp(self):
        self.audio_path = Path(
            settings.APP_DIR,
            'grunt/tests/media/test-audio.wav')

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()

    def make_session(self, game, instructed=False, receipts=[]):
        self.client.get(game.get_absolute_url())
        session = self.client.session
        session['instructed'] = instructed
        session['receipts'] = receipts
        session.save()


class GameListViewTest(ViewTest):
    """ Show all available games """
    game_list_url = reverse('games_list')

    def test_game_list_view_renders_game_list_template(self):
        response = self.client.get(self.game_list_url)
        self.assertTemplateUsed(response, 'grunt/game_list.html')

    def test_games_show_up_on_home_page(self):
        num_games = 10
        expected_games = mommy.make(Game, _quantity = num_games)
        response = self.client.get(self.game_list_url)
        visible_games = response.context['game_list']
        self.assertEqual(len(visible_games), num_games)

    def test_most_recent_games_shown_first(self):
        _, newer_game = mommy.make(Game, _quantity = 2)
        response = self.client.get(self.game_list_url)
        top_game = response.context['game_list'][0]
        self.assertEquals(top_game, newer_game)


class TelephoneViewTest(ViewTest):
    def setUp(self):
        super(PlayViewTest, self).setUp()
        self.game = mommy.make(Game)
        self.game_play_url = reverse('play', pk=self.game.pk)
        self.chain = mommy.make(Chain, game = self.game)
        self.message = mommy.make(Message, chain = self.chain)

    def test_get_instructions_page(self):
        """ First visit should render instructions template. """
        response = self.client.get(self.game_play_url)
        self.assertTemplateUsed(response, 'grunt/instructions.html')

    def test_get_telephone_page(self):
        """ Instructed and mic checked players should get the play template. """
        self.make_session(self.game, instructed=True)
        response = self.client.get(self.game_play_url)
        self.assertTemplateUsed(response, 'grunt/play.html')

    def test_game_is_provided_as_context(self):
        """ The current game should be sent to the template for rendering.

        The game should be sent to both the instructions template and the
        play template.
        """
        response = self.client.get(self.game_play_url)
        self.assertTemplateUsed(response, 'grunt/instructions.html')
        self.assertEquals(response.context['game'], self.game)

        self.make_session(self.game, instructed=True)
        response = self.client.get(self.game_play_url)
        self.assertTemplatedUsed(response, 'grunt/play.html')
        self.assertEquals(response.context['game'], self.game)

class SwitchboardViewTest(ViewTest):
    def setUp(self):
        super(RespondViewTest, self).setUp()
        self.game = mommy.make(Game)
        self.chain = mommy.make(Chain, game = self.game)
        self.message = mommy.make(Message, chain = self.chain)

        self.post_url = reverse('play', kwargs={'pk': self.game.pk})

    def test_exclude_chains_in_session(self):
        """ If there are receipts in the session, get the correct chain """
        second_chain = mommy.make(Chain, game = self.game)
        mommy.make(Message, chain = second_chain)

        self.make_session(self.game, instructed=True, mic_checked=True,
                receipts = [self.chain.pk, ])

        response = self.client.get(self.game.get_absolute_url())

        selected_message = response.context['message']
        self.assertIn(selected_message, second_chain.message_set.all())

    def post_response(self):
        with open(self.audio_path, 'rb') as audio_handle:
            audio_file = File(audio_handle)
            post_data = {'message': self.message.pk, 'audio': audio_file}
            response = self.client.post(self.post_url, post_data)
        return response

    def test_post_a_message(self):
        """ Post a message """
        messages_before_post = Message.objects.count()
        self.post_response()
        self.assertEquals(Message.objects.count(), messages_before_post + 1)

    def test_post_adds_receipt_to_session(self):
        """ Posting an entry adds a receipt to the session """
        self.post_response()
        self.assertIn(self.chain.pk, self.client.session['receipts'])

    def test_invalid_post(self):
        """ Post an entry without a recording """
        invalid_post = {'message': self.message.pk}
        response = self.client.post(self.post_url, invalid_post)
        self.assertEquals(response.status_code, 404)

    def test_posting_with_no_more_entries_returns_completed_flag(self):
        """ Posting an entry should redirect to the completion page """
        self.make_session(self.game, instructed=True, mic_checked=True)
        response = self.post_response()

        response_json = json.loads(response._container[0])
        self.assertEquals(response_json, {'completed': True})

    def test_post_leads_to_next_cluster(self):
        """ Posting a message should redirect to another message """
        second_chain = mommy.make(Chain, game = self.game)
        second_message = mommy.make(Message, chain = second_chain)

        self.make_session(self.game, instructed=True, mic_checked=True)
        response = self.post_response()

        response_json = json.loads(response._container[0])
        new_message_pk = response_json['message']
        self.assertEquals(new_message_pk, second_message.pk)
