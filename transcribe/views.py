from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, CreateView, FormView
from django.contrib import messages

from rest_framework.renderers import JSONRenderer

from grunt.models import MessageSerializer
from .models import TranscriptionSurvey, MessageToTranscribe
from .forms import NewTranscriptionSurveyForm, TranscriptionForm
from .exceptions import *


class TranscriptionSurveyList(ListView):
    model = TranscriptionSurvey
    queryset = TranscriptionSurvey.objects.all().order_by('-id')
    template_name = 'transcribe/survey_list.html'


class NewSurveyView(CreateView):
    template_name = 'transcribe/new_survey.html'
    form_class = NewTranscriptionSurveyForm
    success_url = reverse_lazy('transcribe_list')


class TakeSurveyView(View):
    form_class = TranscriptionForm
    template_name = 'transcribe/form.html'

    def get(self, request, pk):
        survey = get_object_or_404(TranscriptionSurvey, pk=pk)
        receipts = request.session.get('receipts', [])

        try:
            message = survey.pick_next_message(receipts)
        except (SurveyCompleteException, NoMoreMessagesException):
            if len(receipts) > 0:
                completion_code = '-'.join(map(str, receipts))
                request.session['receipts'] = []
                context_data = dict(completion_code=completion_code)
                return render(request, 'ratings/complete.html', context_data)
            else:
                raise Http404('The survey was not configured properly.')

        transcription_form = TranscriptionForm(initial={'message': message})

        # Serialize message as JSON for playing the audio
        message_data = MessageSerializer(message.given).data
        message_json = JSONRenderer().render(message_data)

        context_data = dict(form=transcription_form, message=message_json)
        return render(request, 'transcribe/form.html', context_data)

    def post(self, request, pk):
        survey = get_object_or_404(TranscriptionSurvey, pk=pk)
        receipts = request.session.get('receipts', [])

        transcription_form = TranscriptionForm(request.POST)
        if transcription_form.is_valid():
            transcription = transcription_form.save()
            receipts += [transcription.pk, ]
            request.session['receipts'] = receipts
            validation_msg = 'Your response was saved! Another message was loaded.'
            messages.add_message(request, messages.SUCCESS, validation_msg)
            return redirect('transcribe_messages', pk=pk)
        else:
            message = MessageToTranscribe.objects.get(pk=request.POST['message'])
            transcription_form.initial['message'] = message
            message_data = MessageSerializer(message.given).data
            message_json = JSONRenderer().render(message_data)
            context_data = dict(form=transcription_form, message=message_json)
            return render(request, 'transcribe/form.html', context_data)
