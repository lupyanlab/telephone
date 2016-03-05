from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, CreateView, FormView

from .models import TranscriptionSurvey
from .forms import NewTranscriptionSurveyForm, TranscriptionForm
from .exceptions import *


class TranscriptionSurveyList(ListView):
    model = TranscriptionSurvey
    template_name = 'transcribe/survey_list.html'


class NewSurveyView(CreateView):
    template_name = 'ratings/new_survey.html'
    form_class = NewTranscriptionSurveyForm
    success_url = reverse_lazy('transcribe_list')


class TakeSurveyView(FormView):
    form_class = TranscriptionForm

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

    def form_valid(self, form):
        transcription = form.save()
        receipts = self.request.session.get('receipts', [])
        receipts.append(transcription.pk)
        validation_msg = 'Your response was saved! Another message was loaded.'
        messages.add_message(self.request, messages.SUCCESS, validation_msg)
        return redirect('take_survey', pk=survey.pk)
