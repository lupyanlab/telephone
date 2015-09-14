from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, View

from ratings.models import Survey, Question
from ratings.forms import NewSurveyForm


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
            'completed_questions', list()
        )

        try:
            question = survey.pick_next_question(
                request.session['completed_questions']
            )
        except Question.DoesNotExist:
            return redirect('complete', pk=survey.pk)


class InspectSurveyView(DetailView):
    model = Survey

    def get_context_data(self, **kwargs):
        context_data = super(InspectSurveyView, self).get_context_data(**kwargs)
        context_data['questions'] = context_data['survey'].questions.all()
        return context_data
