from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from rest_framework import viewsets

from grunt.models import Game, Message
from inspector.serializers import GameSerializer, MessageSerializer, MessageDetailsSerializer


class InspectView(TemplateView):
    template_name = 'inspector/inspect.html'

    def get_context_data(self, **kwargs):
        context_data = super(InspectView, self).get_context_data(**kwargs)
        game = get_object_or_404(Game, pk=self.kwargs.get('pk'))
        context_data['game'] = game

        # Calculate some parameters for styling the tree
        # based on the size of the game.
        num_siblings = game.get_messages_by_generation(1).count()
        if num_siblings == 0:
            num_siblings = game.get_messages_by_generation(0).count()
        context_data['num_siblings'] = num_siblings
        context_data['num_generations'] = game.get_max_generation()
        return context_data


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    list_serializer_class = MessageSerializer
    serializer_class = MessageDetailsSerializer

    def get_serializer_class(self):
        """
        Use brief serializer for lists of messages and detailed for all other cases.
        """
        if self.action == 'list':
            return self.list_serializer_class
        else:
            return self.serializer_class


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
