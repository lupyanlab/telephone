
from django.core.urlresolvers import reverse_lazy
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import View, ListView, CreateView, FormView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from .models import Game, Chain, MessageSerializer
from .forms import ResponseForm
from .handlers import check_volume

VOLUME_CUTOFF_dBFS = -30.0


@require_POST
def accept(request, pk):
    """ Record that the player accepted the instructions in the session """
    request.session['instructed'] = True
    return redirect('play', pk=pk)


class TelephoneView(View):
    """ Pick up the phone.

    Either read the instructions or get to the telephone.
    """
    def get(self, request, pk):
        """ Determine what to do when a user requests the game page.

        1. First time users should read the instructions.
        2. Validated users should be given the telephone.
        """
        game = get_object_or_404(Game, pk=pk)

        # Initialize the player's session
        request.session['instructed'] = request.session.get('instructed', False)
        request.session['receipts'] = request.session.get('receipts', [])

        # Check if the player has accepted the instructions
        if not request.session['instructed']:
            return render(request, 'grunt/instructions.html', {'game': game})
        else:
            request.session['instructed'] = True  # don't show these again
            return render(request, 'grunt/play.html', {'game': game})


class SwitchboardView(APIView):
    """ Connect to an ongoing game.

    All messages are communicated in JSON.
    """
    def get(self, request, pk):
        """ A player requests a message for the first time. """
        game = Game.objects.get(pk=pk)
        receipts = request.session.setdefault('receipts', [])
        message = game.pick_next_message(receipts)
        data = MessageSerializer(message).data
        return Response(data)

    def post(self, request, pk):
        """ A player made a message.

        1. Make sure it's loud enough.
        2. Save it, kill the parent, and give them another one.
        """
        if 'audio' not in request.FILES:
            raise APIException()

        audio = request.FILES['audio']
        if check_volume(audio) < VOLUME_CUTOFF_dBFS:
            raise APIException()

        response_form = ResponseForm(request.POST, request.FILES)
        # !!! Assuming the form is valid
        message = response_form.save()

        request.session.setdefault('receipts', []).append(message.pk)

        message.parent.kill()

        try:
            game = Game.objects.get(pk=pk)
            next_message = game.pick_next_message(request.session['receipts'])
            data = MessageSerializer(next_message).data
            return Response(data)
        except IndexError:
            completion_code = '-'.join(map(str, request.session['receipts']))
            return Response({'completion_code': completion_code})


class GameListView(ListView):
    template_name = 'grunt/game_list.html'
    queryset = Game.objects.all().order_by('-id')
