from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from rest_framework import viewsets

from grunt.models import Game, Message
from inspector.serializers import GameSerializer, MessageSerializer


class InspectView(TemplateView):
    template_name = 'inspector/inspect.html'

    def get_context_data(self, **kwargs):
        context_data = super(InspectView, self).get_context_data(**kwargs)
        game = get_object_or_404(Game, pk=self.kwargs.get('pk'))
        context_data['game'] = game
        return context_data


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
