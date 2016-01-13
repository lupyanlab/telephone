from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from unipath import Path
from model_mommy import mommy

from grunt.models import Game, Chain, Message
from grunt.forms import NewGameForm

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ViewTest(TestCase):
    def setUp(self):
        self.audio_path = Path(
            settings.APP_DIR,
            'grunt/tests/media/test-audio.wav')

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()

    def make_session(self, game, instructed=False, receipts=None):
        game_url = reverse('play', kwargs={'pk': game.pk})
        self.client.get(game_url)
        session = self.client.session
        session['instructed'] = instructed

        if not receipts:
            receipts = list()
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
        mommy.make(Game, _quantity=num_games)
        response = self.client.get(self.game_list_url)
        visible_games = response.context['game_list']
        self.assertEqual(len(visible_games), num_games)

    def test_most_recent_games_shown_first(self):
        _, newer_game = mommy.make(Game, _quantity=2)
        response = self.client.get(self.game_list_url)
        top_game = response.context['game_list'][0]
        self.assertEquals(top_game, newer_game)


class TelephoneViewTest(ViewTest):
    def setUp(self):
        super(TelephoneViewTest, self).setUp()
        self.game = mommy.make(Game)
        self.game_play_url = reverse('play', kwargs={'pk': self.game.pk})
        self.chain = mommy.make(Chain, game=self.game)
        self.message = mommy.make(Message, chain=self.chain)

    def test_get_instructions_page(self):
        """ First visit should render instructions template. """
        response = self.client.get(self.game_play_url)
        self.assertTemplateUsed(response, 'grunt/instructions.html')

    def test_get_telephone_page(self):
        """ Instructed players should get the play template. """
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
        self.assertTemplateUsed(response, 'grunt/play.html')
        self.assertEquals(response.context['game'], self.game)


class SwitchboardViewTest(ViewTest):
    def setUp(self):
        super(SwitchboardViewTest, self).setUp()
        self.game = mommy.make(Game)
        self.chain = mommy.make(Chain, game=self.game)
        self.message = mommy.make(Message, chain=self.chain)

        self.switchboard_url = reverse('switchboard',
                                       kwargs={'pk': self.game.pk})

    def test_successful_post_returns_next_message(self):
        second_chain = mommy.make(Chain, game=self.game)
        second_message = mommy.make(Message, chain=second_chain)

        self.make_session(self.game, instructed=True,
                          receipts=[self.message.pk, ])

        response = self.client.get(self.switchboard_url)
        self.assertEquals(response.data['id'], second_message.id)

    def test_exclude_chains_in_session(self):
        """ If there are receipts in the session, get the correct chain """
        second_chain = mommy.make(Chain, game=self.game)
        mommy.make(Message, chain=second_chain)

        self.make_session(self.game, instructed=True,
                          receipts=[self.message.pk, ])

        response = self.client.get(self.switchboard_url)
        selected_message_id = response.data['id']
        self.assertIn(selected_message_id,
                      second_chain.messages.values_list('id', flat=True))

    def post_response(self):
        with open(self.audio_path, 'rb') as audio_handle:
            audio_file = File(audio_handle)
            post_data = {'parent': self.message.pk, 'audio': audio_file}
            response = self.client.post(self.switchboard_url, post_data)
        return response

    def test_post_a_message(self):
        """ Post a message """
        messages_before_post = Message.objects.count()
        self.post_response()
        self.assertEquals(Message.objects.count(), messages_before_post + 1)

    def test_post_adds_receipt_to_session(self):
        """ Posting an entry adds a receipt to the session """
        self.post_response()
        self.assertEquals(len(self.client.session['receipts']), 1)

    def test_invalid_post(self):
        """ Post an entry without a recording """
        invalid_post = {'audio': self.message.pk}
        response = self.client.post(self.switchboard_url, invalid_post)
        self.assertEquals(response.status_code, 500)


class NewGameViewTest(ViewTest):
    new_game_url = reverse('new_game')

    def test_new_game_view_renders_new_game_form(self):
        response = self.client.get(self.new_game_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NewGameForm)

    def test_create_new_game(self):
        game_data = dict(name='New game!', num_chains=1, num_seeds_per_chain=1)
        self.client.post(self.new_game_url, game_data)
        new_game = Game.objects.last()
        self.assertEquals(new_game.name, game_data['name'])

    def test_create_new_game_redirects_to_new_chains_view(self):
        game_data = dict(name='New game!', num_chains=1, num_seeds_per_chain=1)
        response = self.client.post(self.new_game_url, game_data)
        base_url = reverse('new_chains', kwargs={'pk': Game.objects.last().pk})
        expected_url = base_url + '?num_chains=1&num_seeds_per_chain=1'
        self.assertRedirects(response, expected_url)

    def test_add_new_chains_view_includes_formset_in_context(self):
        game = mommy.make(Game)
        add_chains_url = reverse('new_chains', kwargs={'pk': game.pk})
        response = self.client.get(add_chains_url)
        self.assertIn('formset', response.context)

    def test_add_new_chains_view_includes_game_in_context(self):
        game = mommy.make(Game)
        add_chains_url = reverse('new_chains', kwargs={'pk': game.pk})
        response = self.client.get(add_chains_url)
        self.assertIn('game', response.context)
        self.assertEquals(response.context['game'], game)

    def test_add_new_chains_view_includes_correct_number_of_chain_forms(self):
        game = mommy.make(Game)
        num_chains_to_add = 10
        add_chains_url = '{}?num_chains={}'.format(
            reverse('new_chains', kwargs={'pk': game.pk}),
            num_chains_to_add
        )
        response = self.client.get(add_chains_url)
        self.assertEquals(len(response.context['formset']), num_chains_to_add)

    def test_add_new_chains_view_prepopulates_correct_game(self):
        game = mommy.make(Game)
        add_chains_url = reverse('new_chains', kwargs={'pk': game.pk})
        response = self.client.get(add_chains_url)
        for form in response.context['formset']:
            self.assertEquals(form.initial['game'], game.pk)

    def test_add_new_chains_with_formset(self):
        game = mommy.make(Game)
        add_chains_url = reverse('new_chains', kwargs={'pk': game.pk})
        new_chain_name = 'new chain name'
        with open(self.audio_path, 'rb') as audio_handle:
            audio_file = File(audio_handle)
            new_chain_formset_data = {
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
                'form-0-game': game.pk,
                'form-0-name': new_chain_name,
                'form-0-seed0': audio_file
            }
            self.client.post(add_chains_url, new_chain_formset_data)

        self.assertEquals(game.chains.count(), 1)
        chain = game.chains.first()
        self.assertEquals(chain.name, new_chain_name)
        self.assertEquals(chain.messages.count(), 1)

    def test_add_new_chains_with_multiple_seeds(self):
        game = mommy.make(Game)
        add_chains_url = reverse('new_chains', kwargs={'pk': game.pk})
        add_chains_url += '?num_seeds_per_chain=2'
        new_chain_name = 'new chain name'

        seed0 = File(open(self.audio_path, 'rb'))
        seed1 = File(open(self.audio_path, 'rb'))

        new_chain_formset_data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
            'form-0-game': game.pk,
            'form-0-name': new_chain_name,
            'form-0-seed0': seed0,
            'form-0-seed1': seed1,
        }

        self.client.post(add_chains_url, new_chain_formset_data)

        seed0.close()
        seed1.close()

        self.assertEquals(game.chains.count(), 1)
        chain = game.chains.first()
        self.assertEquals(chain.name, new_chain_name)
        self.assertEquals(chain.messages.count(), 2)
