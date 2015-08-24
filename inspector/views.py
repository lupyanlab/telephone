import json
from unipath import Path
import StringIO
import zipfile

from django.http import JsonResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView, UpdateView

from grunt.models import Game, Message
from inspector.forms import UploadMessageForm


class InspectView(DetailView):
    template_name = 'inspector/inspect.html'
    model = Game


class UploadMessageView(UpdateView):
    model = Message
    form_class = UploadMessageForm
    template_name = 'inspector/upload-message.html'

    def get_form(self, form_class):
        """ Populate the form's action attribute with the correct url """
        form = super(UploadMessageView, self).get_form(form_class)
        message_pk = form.instance.pk
        form.helper.form_action = reverse('upload', kwargs={'pk': message_pk})
        return form


@require_GET
def message_data(request, pk):
    game = Game.objects.get(pk=pk)
    ordered_chain_set = game.chain_set.all().order_by('pk')
    requested_chain_ix = int(request.GET['chain'])
    requested_chain = ordered_chain_set[requested_chain_ix]
    message_data = requested_chain.nest()
    return JsonResponse(json.dumps(message_data), safe=False)


@require_POST
def sprout(request, pk):
    message = get_object_or_404(Message, pk=pk)
    message.replicate()

    message_data = message.chain.nest()
    return JsonResponse(json.dumps(message_data), safe=False)


@require_POST
def close(request, pk):
    message = get_object_or_404(Message, pk=pk)
    chain = message.chain
    message.delete()

    message_data = chain.nest()
    return JsonResponse(json.dumps(message_data), safe=False)


def download(request):
    selection_query = request.POST['selection']
    selection_str = selection_query.split(',')
    selection = map(int, selection_str)
    messages = Message.objects.filter(id__in=selection)

    s = StringIO.StringIO()
    zf = zipfile.ZipFile(s, "w")

    # Name the root directory in the zip based on the game name
    root_dirname = messages[0].chain.game.dirname()

    for msg in messages:
        audio_path = msg.audio.path

        msg_name_format = "{generation}-{parent}-{message}.wav"
        msg_name_kwargs = {}
        msg_name_kwargs['generation'] = 'gen' + str(msg.generation)
        msg_name_kwargs['message'] = 'message' + str(msg.id)

        if not msg.parent:
            msg_name_kwargs['parent'] = 'seed'
        else:
            msg_name_kwargs['parent'] = 'parent' + str(msg.parent.id)

        msg_name = msg_name_format.format(**msg_name_kwargs)
        msg_path = Path(root_dirname, msg_name)

        zf.write(audio_path, msg_path)

    zf.close()

    response = HttpResponse(s.getvalue(),
                            content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename="messages.zip"'
    return response
