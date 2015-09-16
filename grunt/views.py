
from django.core.urlresolvers import reverse_lazy
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import View, ListView, CreateView, FormView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from .models import Game, Chain
from .forms import NewGameForm, NewChainForm, NewChainFormsetHelper, ResponseForm
from .handlers import check_volume

VOLUME_CUTOFF_dBFS = -20.0


class GameListView(ListView):
    template_name = 'grunt/games.html'
    queryset = Game.objects.all().order_by('-id')


class NewGameView(CreateView):
    template_name = 'grunt/new_game.html'
    form_class = NewGameForm

    def form_valid(self, form):
        """ Save the game form and redirect to the chain forms. """
        self.object = form.save()
        num_chain_forms = form.cleaned_data['num_chains']
        url = self.get_success_url() + '?chains={}'.format(num_chain_forms)
        return HttpResponseRedirect(url)

    def get_success_url(self):
        return reverse_lazy('add_chain', kwargs={'pk': self.object.pk})


class AddChainView(FormView):
    template_name = 'grunt/new_chain.html'

    def get_form(self):
        self.game = get_object_or_404(Game, pk=self.kwargs['pk'])
        num_chain_forms = self.request.GET.get('chains', 1)
        try:
            num_chain_forms = int(num_chain_forms)
        except ValueError:
            num_chain_forms = 1

        kwargs = {'fields': ('name', 'audio'), 'extra': num_chain_forms}
        AddChainFormset = inlineformset_factory(Chain, Game, **kwargs)
        formset = AddChainFormset(instance=game)
        return formset

    def get_context_data(self, **kwargs):
        context_data = super(AddChainView, self).get_context_data(**kwargs)
        context_data.update({
            'game': self.game,
            'formset': context_data['form'],
            'helper': NewChainFormsetHelper(),
        })
        return context_data

    def form_valid(self, form):
        print 'it was good'
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        print form.errors
        print 'it was bad'

    def get_success_url(self):
        return reverse_lazy('view_game', kwargs={'pk': self.kwargs['pk']})


@require_POST
def accept(request, pk):
    """ Record that the player accepted the instructions in the session """
    request.session['instructed'] = True
    return redirect('play_game', pk=pk)


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


class SwitchboardView(APIView):
    """ Connect to an ongoing game.

    All messages are communicated in JSON.
    """
    def get(self, request, pk):
        """ A player is checking in with her receipts.

        1. Give her another message.
        2. If there aren't any messages for her, she's done.
        """
        game = Game.objects.get(pk=pk)
        request.session['receipts'] = request.session.get('receipts', [])
        try:
            message = game.pick_next_message(request.session['receipts'])
            return Response(message)
        except Chain.DoesNotExist:
            return Response()

    def post(self, request, pk):
        """ A player made a message.

        1. Make sure it's loud enough.
        2. Save it, and kill the parent.
        """
        audio = request.FILES['audio']
        if check_volume(audio) < VOLUME_CUTOFF_dBFS:
            raise APIException('Your recording was not loud enough. '
                               'Really let it out this time.')

        response_form = ResponseForm(request.POST, request.FILES)

        if response_form.is_valid():
            message = response_form.save()

            receipts = request.session.get('receipts', [])
            receipts.append(message.pk)
            request.session['receipts'] = receipts

            message.parent.kill()
            return Response()
        else:
            return Response(response_form.errors)
