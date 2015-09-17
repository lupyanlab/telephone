from django.views.generic import DetailView

from rest_framework.views import APIView
from rest_framework.response import Response

from grunt.models import Game
from inspector.serializers import GameSerializer


class InspectView(DetailView):
    template_name = 'inspector/inspect.html'
    model = Game


class MessageTreeAPIView(APIView):
    def get(self, request, pk):
        game = Game.objects.get(pk=pk)
        tree = GameSerializer(game).data
        return Response(tree)
