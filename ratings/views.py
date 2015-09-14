from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.views.generic import ListView, CreateView, DetailView, View
from django.shortcuts import get_object_or_404, render, redirect

from ratings.models import Survey, Question
from ratings.forms import NewSurveyForm, ResponseForm


class SurveyList(ListView):
    model = Survey


class NewSurveyView(CreateView):
    template_name = 'ratings/new_survey.html'
    form_class = NewSurveyForm
    success_url = reverse_lazy('survey_list')


class TakeSurveyView(View):
    def get(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)

        # Initialize the survey taker's session
        request.session['completed_questions'] = request.session.get(
            'completed_questions', []
        )
        request.session['receipts'] = request.session.get('receipts', [])


        try:
            question = survey.pick_next_question(
                request.session['completed_questions']
            )
            response_form = ResponseForm(initial = {'question': question})
            response_form.fields['selection'].empty_label = None
            response_form.fields['selection'].queryset = question.choices.all()
            context_data = {
                'question': question,
                'choices': question.choices.all(),
                'form': response_form
            }
            return render(request, 'ratings/question.html', context_data)
        except Question.DoesNotExist:
            receipts = request.session['receipts']
            if receipts:
                completion_code = '-'.join(map(str, receipts))
                context_data = {'completion_code': completion_code}
                return render(request, 'ratings/complete.html', context_data)
            else:
                raise Http404('No receipts found')

    def post(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)

        request.session['receipts'] = request.session.get('receipts', [])

        response_form = ResponseForm(request.POST)
        if response_form.is_valid():
            response = response_form.save()
            request.session['receipts'].append(response.pk)
            return redirect('take_survey', pk=survey.pk)
        else:
            question = Question.objects.get(pk=request.POST['question'])
            context_data = {
                'question': question,
                'form': response_form,
            }
            return render(request, 'ratings/question.html', context_data)


class InspectSurveyView(DetailView):
    model = Survey

    def get_context_data(self, **kwargs):
        context_data = super(InspectSurveyView, self).get_context_data(**kwargs)
        context_data['questions'] = context_data['survey'].questions.all()
        return context_data
