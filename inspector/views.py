from django.views.generic import DetailView

from rest_framework.views import APIView

from grunt.models import Game
from inspector.serializers import ChainSerializer


class InspectView(DetailView):
    template_name = 'inspector/inspect.html'
    model = Game


class MessageTreeAPIView(APIView):
    def get(self, request, pk):
        game = Game.objects.get(pk=pk)
        trees = [ChainSerializer(chain).data for chain in game.chains.all()]
        return Response(trees)
