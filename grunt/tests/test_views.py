import json

from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from unipath import Path
from model_mommy import mommy

from grunt.forms import NewGameForm
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

    def make_session(self, game, instructed=False, mic_checked=False,
                     receipts=list(), messages=list()):
        self.client.get(game.get_absolute_url())
        session = self.client.session
        session['instructed'] = instructed
        session['mic_checked'] = mic_checked
        session['receipts'] = receipts
        session['messages'] = messages
        session.save()


class GamesViewTest(ViewTest):
    """ Show all available games """
    games_list_url = reverse('games_list')

    def test_game_list_view_renders_game_list_template(self):
        response = self.client.get(self.games_list_url)
        self.assertTemplateUsed(response, 'grunt/games.html')

    def test_games_show_up_on_home_page(self):
        """ Games should be listed on the home page """
        num_games = 10
        expected_games = mommy.make(Game, _quantity = num_games)
        response = self.client.get(self.games_list_url)
        visible_games = response.context['game_list']
        self.assertEqual(len(visible_games), num_games)

    def test_inactive_games_not_shown(self):
        """ Games can be active or inactive """
        inactive_games = mommy.make(Game, status = "INACT", _quantity = 10)
        response = self.client.get(self.games_list_url)
        self.assertEqual(len(response.context['game_list']), 0)

    def test_most_recent_games_shown_first(self):
        """ The newest games should be shown at the top """
        _, newer_game = mommy.make(Game, _quantity = 2)
        response = self.client.get(self.games_list_url)
        top_game = response.context['game_list'][0]
        self.assertEquals(top_game, newer_game)


class NewGameViewTest(ViewTest):
    def test_new_game_page_renders_new_game_form(self):
        """ Simple, standalone page to make a new game """
        new_game_page_url = reverse('new_game')
        response = self.client.get(new_game_page_url)
        form_in_response = response.context['form']
        self.assertIsInstance(form_in_response, NewGameForm)


class PlayViewTest(ViewTest):
    def setUp(self):
        super(PlayViewTest, self).setUp()
        self.game = mommy.make(Game)
        self.chain = mommy.make(Chain, game = self.game)
        self.message = mommy.make(Message, chain = self.chain)

    def test_instructions_page(self):
        """ First visit should render instructions template """
        response = self.client.get(self.game.get_absolute_url())
        self.assertTemplateUsed(response, 'grunt/instruct.html')

    def test_mic_check_page(self):
        """ After accepting instructions players should see a mic check page """
        self.make_session(self.game, instructed=True)
        response = self.client.get(self.game.get_absolute_url())
        self.assertTemplateUsed(response, 'grunt/mic_check.html')

    def test_get_game_play_page(self):
        """ Instructed and mic checked players should get the play template """
        self.make_session(self.game, instructed=True, mic_checked=True)
        response = self.client.get(self.game.get_absolute_url())
        self.assertTemplateUsed(response, 'grunt/play.html')

    def test_initial_message_data(self):
        """ The template should be populated with the correct message obj """
        self.make_session(self.game, instructed=True, mic_checked=True)
        response = self.client.get(self.game.get_absolute_url())

        initial_message = response.context['message']
        self.assertEquals(initial_message, self.message)

    def test_exclude_chains_in_session(self):
        """ If there are receipts in the session, get the correct chain """
        second_chain = mommy.make(Chain, game = self.game)
        mommy.make(Message, chain = second_chain)

        self.make_session(self.game, instructed=True, mic_checked=True,
                receipts = [self.chain.pk, ])

        response = self.client.get(self.game.get_absolute_url())

        selected_message = response.context['message']
        self.assertIn(selected_message, second_chain.message_set.all())

    def test_redirect_to_completion_page_on_return_visit(self):
        """ Completed players should get the completion page """
        self.make_session(self.game, instructed=True, mic_checked=True,
                          receipts = [self.chain.pk, ])
        response = self.client.get(self.game.get_absolute_url())

        complete_url = reverse('complete', kwargs = {'pk': self.game.pk})
        self.assertRedirects(response, complete_url)


class RespondViewTest(ViewTest):
    post_url = reverse('respond')

    def setUp(self):
        super(RespondViewTest, self).setUp()
        self.game = mommy.make(Game)
        self.chain = mommy.make(Chain, game = self.game)
        self.message = mommy.make(Message, chain = self.chain)

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

    def test_posting_with_no_more_entries_returns_empty_json(self):
        """ Posting an entry should redirect to the completion page """
        self.make_session(self.game, instructed=True, mic_checked=True)
        response = self.post_response()

        response_json = json.loads(response._container[0])
        self.assertEquals(response_json, dict())

    def test_post_leads_to_next_cluster(self):
        """ Posting a message should redirect to another message """
        second_chain = mommy.make(Chain, game = self.game)
        second_message = mommy.make(Message, chain = second_chain)

        self.make_session(self.game, instructed=True, mic_checked=True)
        response = self.post_response()

        response_json = json.loads(response._container[0])
        new_message_pk = response_json['message']
        self.assertEquals(new_message_pk, second_message.pk)


class CompletionViewTest(ViewTest):
    def setUp(self):
        super(CompletionViewTest, self).setUp()
        self.game = mommy.make(Game)
        self.chain = mommy.make(Chain, game = self.game)
        self.message = mommy.make(Message, chain = self.chain)
        self.complete_url = reverse('complete', kwargs = {'pk': self.game.pk})

    def test_completion_view_renders_complete_template(self):
        response = self.client.get(self.complete_url)
        self.assertTemplateUsed(response, 'grunt/complete.html')

    def test_completion_code_contains_message_receipts(self):
        simulated_messages = [1,2,3]
        self.make_session(self.game, messages = simulated_messages)
        response = self.client.get(self.complete_url)
        completion_code = response.context['completion_code']
        for msg in simulated_messages:
            self.assertIn(str(msg), completion_code)
