from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView, CreateView, DetailView

from .models import Game, Chain, Message
from .forms import NewGameForm
from .handlers import check_volume


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


class CompletionView(DetailView):
    template_name = 'grunt/complete.html'
    model = Game

    def get_context_data(self, **kwargs):
        context_data = super(CompletionView, self).get_context_data(**kwargs)
        game = context_data['game']
        message_receipts = self.request.session.get('messages', list())
        receipt_code = '-'.join(map(str, message_receipts))
        completion_code = 'G{pk}-{receipts}'.format(pk=game.pk,
                                                    receipts=receipt_code)
        context_data['completion_code'] = completion_code
        return context_data


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


@require_GET
def play_game(request, pk):
    """ Determine what to do when a user requests the game page.

    1. First time users should read the instructions and complete a
       microphone check.
    2. Validated users should be selected a message to view and respond to.
    """
    game = get_object_or_404(Game, pk=pk)

    # Initialize the player's session
    request.session['instructed'] = request.session.get('instructed', False)
    request.session['mic_checked'] = request.session.get('mic_checked', False)
    request.session['receipts'] = request.session.get('receipts', list())
    request.session['messages'] = request.session.get('messages', list())

    # Check if the player has accepted the instructions
    if not request.session['instructed']:
        return render(request, 'grunt/instruct.html', {'game': game})

    # Check if the user has completed a microphone check
    if not request.session['mic_checked']:
        print 'mic not checked'
        return render(request, 'grunt/mic_check.html', {'game': game})

    try:
        chain = game.pick_next_chain(request.session['receipts'])
        message = chain.select_empty_message()
    except Chain.DoesNotExist:
        # It's likely that this player has already played the game
        # and returned to play it again without clearing the session.
        return redirect('complete', pk=game.pk)
    except Message.DoesNotExist:
        # Something weird happened
        raise Http404("The game is not configured properly.")

    context_data = {'game': game, 'message': message}
    return render(request, 'grunt/play.html', context_data)


@require_POST
def clear(request, pk):
    request.session['instructed'] = False
    request.session['receipts'] = list()
    request.session['messages'] = list()
    return redirect('complete', pk=pk)


@require_POST
def respond(request):
    pk = request.POST['message']
    try:
        message = Message.objects.get(pk=pk)

        # If the message already has an audio file, (i.e., someone
        # has already submitted a response), then create a new
        # branch from the parent, and add the new audio to that.
        if message.audio:
            parent = message.parent
            message = parent.replicate()

        # Update the message with the newly recorded audio
        message.audio = request.FILES.get('audio', None)
        if not message.audio:
            raise Http404('No message attached to post')

        message.save()
        message.replicate()

        # Add the successful message chain to session receipts
        receipts = request.session.get('receipts', list())
        receipts.append(message.chain.pk)
        request.session['receipts'] = receipts

        # Add the message to the message receipts
        message_receipts = request.session.get('messages', list())
        message_receipts.append(message.pk)
        request.session['messages'] = message_receipts

        # Search for the next message
        game = message.chain.game
        next_chain = game.pick_next_chain(receipts)
        next_message = next_chain.select_empty_message()

        data = {'message': next_message.pk}
        if next_message.parent and next_message.parent.audio:
            data['src'] = next_message.parent.audio.url
    except Message.DoesNotExist:
        # Something weird happened.
        data = {}
    except Chain.DoesNotExist:
        # There are no more chains for this player to respond to.
        # Returning an empty response will redirect the player
        # to the completion page.
        data = {}

    return JsonResponse(data)
