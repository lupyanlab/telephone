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


@require_POST
def mic_check(request, pk):
    recording = request.FILES.get('audio', None)
    mic_checked = check_volume(recording)
    request.session['mic_checked'] = mic_checked
    return JsonResponse({'mic_checked': mic_checked})

class PlayGameView(View):
    def get(self, request, pk):
        """ Determine what to do when a user requests the game page.

        1. First time users should read the instructions and complete a
           microphone check.
        2. Validated users should be selected a message to view and respond to.
        """
        game = get_object_or_404(Game, pk=pk)

        # Initialize the player's session
        request.session['instructed'] = request.session.get('instructed', False)
        request.session['receipts'] = request.session.get('receipts', list())
        request.session['messages'] = request.session.get('messages', list())

        # Check if the player has accepted the instructions
        if not request.session['instructed']:
            return render(request, 'grunt/instruct.html', {'game': game})

        try:
            chain = game.pick_next_chain(request.session['receipts'])
            message = chain.select_empty_message()
        except Chain.DoesNotExist:
            # It's likely that this player has already played the game
            # and returned to play it again without clearing the session.
            completion_code = get_completion_code(request)
            request = clear_receipts_from_session(request)
            return render(request, 'grunt/complete.html',
                          {'game': game, 'completion_code': completion_code})
        except Message.DoesNotExist:
            # Something weird happened
            raise Http404("The game is not configured properly.")

        context_data = {'game': game, 'message': message}
        return render(request, 'grunt/play.html', context_data)

    def post(self, request, pk):
        game = get_object_or_404(Game, pk=pk)
        message = get_object_or_404(Message, pk=request.POST['message'])

        # If the message already has an audio file, (i.e., someone
        # has already submitted a response), then create a new
        # branch from the parent, and add the new audio to that.
        if message.audio:
            parent = message.parent
            message = parent.replicate()

        # Update the message with the newly recorded audio
        audio = request.FILES.get('audio', None)
        if not audio:
            raise Http404('No message attached to post')

        # Check the volume
        volume = check_volume(audio)
        if volume < VOLUME_CUTOFF_dBFS:
            mic_check_error = ('Your recording was not loud enough. '
                               'Please try again.')
            messages.add_message(request, messages.ERROR, mic_check_error)

            data = {'msg': render_to_string('_messages.html', {},
                           RequestContext(request))}
            return JsonResponse(data, safe=False)

        message.audio = audio
        message.save()
        message.replicate()

        # Add the successful message chain to session receipts
        receipts = request.session.get('receipts', [])
        receipts.append(message.chain.pk)
        request.session['receipts'] = receipts

        # Add the message to the message receipts
        message_receipts = request.session.get('messages', [])
        message_receipts.append(message.pk)
        request.session['messages'] = message_receipts

        # Search for the next message
        game = message.chain.game
        try:
            next_chain = game.pick_next_chain(receipts)
            next_message = next_chain.select_empty_message()

            data = {'message': next_message.pk}
            if next_message.parent and next_message.parent.audio:
                data['src'] = next_message.parent.audio.url

            receipt_msg = ('Your message was received. '
                           'A new message was loaded.')
            messages.add_message(request, messages.SUCCESS, receipt_msg)
            data['msg'] = render_to_string('_messages.html', {},
                                           RequestContext(request))
            return JsonResponse(data, safe=False)
        except Chain.DoesNotExist:
            # There are no more chains for this player to respond to.
            # Returning an empty response will redirect the player
            # to the completion page.
            return JsonResponse({'completed': True})
        except Message.DoesNotExist:
            # Something weird happened.
            return Http404("Game is improperly configured")


def get_completion_code(request):
    message_receipts = request.session.get('messages', [])
    completion_code = '-'.join(map(str, message_receipts))
    return completion_code

def clear_receipts_from_session(request):
    request.session['receipts'] = []
    return request
