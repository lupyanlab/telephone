from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from grunt.models import Game
from inspector.serializers import GameSerializer


class InspectView(TemplateView):
    template_name = 'inspector/inspect.html'

    def get_context_data(self, **kwargs):
        context_data = super(InspectView, self).get_context_data(**kwargs)
        game = get_object_or_404(Game, pk=self.kwargs.get('pk'))
        serializer = GameSerializer(game)
        jsoned = JSONRenderer().render(serializer.tree_data)
        context_data['game_tree'] = jsoned
        return context_data


class MessageTreeAPIView(APIView):
    def get(self, request, pk):
        game = Game.objects.get(pk=pk)
        tree = GameSerializer(game).data
        return Response(tree)
