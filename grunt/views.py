import json

from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import View, ListView, CreateView, DetailView

from .models import Game, Chain, Message
from .forms import NewGameForm
from .handlers import check_volume

VOLUME_CUTOFF_dBFS = -20.0


class GameListView(ListView):
    template_name = 'grunt/games.html'
    model = Game

    def get_queryset(self):
        """ Show active games with newest games first """
        active_games = self.model._default_manager.filter(status='ACTIV')
        newest_first = active_games.order_by('-id')
        return newest_first


class NewGameView(CreateView):
    template_name = 'grunt/new-game.html'
    form_class = NewGameForm
    success_url = '/'


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

        # Check if the player has accepted the instructions
        if not request.session['instructed']:
            return render(request, 'grunt/instruct.html', {'game': game})
        else:
            return render(request, 'grunt/play.html', {'game': game})

class SwitchboardView(View):
    """ Connect to an ongoing game.

    All messages are communicated in JSON.
    """
    def get(self, request, pk):
        """ A player is checking in with her receipts.

        1. Give her another message.
        2. If there aren't any messages for her, she's done.
        """
        telephone = {
            'chain_receipts': request.GET.get('chain_receipts', ''),
            'message_receipts': request.GET.get('message_receipts', ''),
        }

        game = Game.objects.get(pk=pk)

        try:
            # Determine next chain based on chain receipts
            receipts = []
            if telephone['chain_receipts']:
                receipts.extend(map(int, telephone['chain_receipts'].split('-')))
            chain = game.pick_next_chain(receipts)
            message = chain.select_empty_message()
            message_data = message.as_dict()
            telephone['message_url'] = message_data['audio']
            telephone['message_pk'] = message_data['pk']
        except Chain.DoesNotExist:
            # No more chains. Player is done!
            telephone['chain_receipts'] = ''
            telephone['completion_code'] = make_completion_code(
                telephone['message_receipts']
            )

        return JsonResponse(telephone)

    def post(self, request, pk):
        """ A player made a message.

        1. Make sure it's loud enough.
        2. Save it, and send them their next message.

        If the message he is responding to is not empty, sprout a new
        branch from the parent message and fill that one.

        The message sprouts a child when it is saved.

        Receipt of a sucessful response is stored in the player's session.
        """
        telephone = {
            'chain_receipts': request.POST.get('chain_receipts', ''),
            'message_receipts': request.POST.get('message_receipts', ''),
        }

        audio = request.FILES.get('recording')
        if check_volume(audio) < VOLUME_CUTOFF_dBFS:
            telephone['error'] = ('Your recording was not loud enough. '
                                  'Really let it out this time.')

            # Give back the same message they were on before
            telephone['message_pk'] = request.POST.get('message_pk')
            telephone['message_url'] = request.POST.get('message_url')

            return JsonResponse(telephone)

        message = Message.objects.get(pk=request.POST.get('message_pk'))
        if message.audio:
            parent = message.parent
            message = parent.replicate()

        message.audio = audio
        message.save()
        message.replicate()

        # Add the successful message chain to session receipts
        if telephone['chain_receipts']:
            receipts = map(int, telephone['chain_receipts'].split('-'))
            receipts.append(message.chain.pk)
        else:
            receipts = [message.chain.pk, ]
        telephone['chain_receipts'] = '-'.join(map(str, receipts))

        if telephone['message_receipts']:
            receipts = map(int, telephone['message_receipts'].split('-'))
            receipts.append(message.pk)
        else:
            receipts = [message.pk, ]
        telephone['message_receipts'] = '-'.join(map(str, receipts))

        # Clear the current message
        telephone['message_pk'] = ''
        telephone['message_url'] = ''

        return JsonResponse(telephone)

def make_completion_code(message_receipts):
    return '-'.join(map(str, message_receipts))

def clear_receipts_from_session(request):
    request.session['receipts'] = []
    return request
