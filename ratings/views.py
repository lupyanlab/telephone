from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response, redirect
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
            'completed_questions', []
        )
        request.session['receipts'] = request.session.get('receipts', [])


        try:
            question = survey.pick_next_question(
                request.session['completed_questions']
            )
            context_data = {'question': question}
            return render_to_response('ratings/question.html', context_data)
        except Question.DoesNotExist:
            receipts = request.session['receipts']
            if receipts:
                completion_code = '-'.join(map(str, receipts))
                context_data = {'completion_code': completion_code}
                return render_to_response('ratings/complete.html', context_data)
            else:
                raise Http404('No receipts found')

    def post(self, request, pk):
        pass


class InspectSurveyView(DetailView):
    model = Survey

    def get_context_data(self, **kwargs):
        context_data = super(InspectSurveyView, self).get_context_data(**kwargs)
        context_data['questions'] = context_data['survey'].questions.all()
        return context_data
