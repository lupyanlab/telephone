from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from grunt.models import Game


class InspectViewTest(TestCase):

    def setUp(self):
        game = mommy.make(Game)
        self.inspect_game_url = reverse('inspect', kwargs={'pk': game.pk})

    def test_inspect_template(self):
        """ Inspecting a game uses the inspect.html template. """
        response = self.client.get(self.inspect_game_url)
        self.assertTemplateUsed(response, 'inspector/inspect.html')

    def test_game_in_context(self):
        """ The game should be sent to the template for rendering. """
        response = self.client.get(self.inspect_game_url)
        self.assertIn('game', response.context)
