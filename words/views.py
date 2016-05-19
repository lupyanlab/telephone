import string

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import Http404
from django.views.generic import ListView, CreateView, View
from django.core.urlresolvers import reverse_lazy

from rest_framework.renderers import JSONRenderer

from words.models import Survey, Question
from words.forms import NewWordSurveyForm, ResponseForm

class WordSurveyList(ListView):
    model = Survey
    queryset = Survey.objects.all().order_by('-id')
    template_name = 'words/survey_list.html'


class NewSurveyView(CreateView):
    template_name = 'words/new_survey.html'
    form_class = NewWordSurveyForm
    success_url = reverse_lazy('words_list')


class TakeWordsSurveyView(View):
    def get(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        request.session['receipts'] = request.session.get('receipts', [])

        try:
            question = survey.pick_next_question(request.session['receipts'])
        except Question.DoesNotExist:
            if request.session['receipts']:
                completion_code = '-'.join(map(str, request.session['receipts']))
                request.session['receipts'] = []
                context_data = {'completion_code': completion_code}
                return render(request, 'words/complete.html', context_data)
            else:
                raise Http404('The survey was not configured properly.')

        response_form = ResponseForm(initial = {'question': question})
        form = self.prepare_response_form(response_form)

        context_data = {'form': form}

        # Serialize choice messages as JSON for playing the audio
        choices_data = MessageSerializer(question.choices.all(), many=True).data
        context_data['choices'] = JSONRenderer().render(choices_data)

        return render(request, 'words/survey.html', context_data)

    def post(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)

        request.session['receipts'] = request.session.get('receipts', [])

        response_form = ResponseForm(request.POST)
        if response_form.is_valid():
            response = response_form.save()
            request.session['receipts'].append(response.pk)

            validation_msg = ('Your response was saved! '
                              'Another message was loaded.')
            messages.add_message(request, messages.SUCCESS, validation_msg)
            return redirect('take_survey', pk=survey.pk)
        else:
            question = Question.objects.get(pk=request.POST['question'])

            response_form.initial['question'] = question
            fresh_form = self.prepare_response_form(response_form)

            context_data = {'form': fresh_form}

            # Serialize choice messages as JSON for playing the audio
            choices_data = MessageSerializer(question.choices.all(), many=True).data
            context_data['choices'] = JSONRenderer().render(choices_data)

            return render(request, 'words/survey.html', context_data)

    def prepare_response_form(self, form):
        message_choices = form.initial['question'].choices.all()
        form.fields['selection'].queryset = message_choices
        choice_labels = list(string.letters[:len(message_choices)])
        choice_map = [(message.id, label) for message, label in zip(message_choices, choice_labels)]
        form.fields['selection'].widget.choices = choice_map
        return form
