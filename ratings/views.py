from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, CreateView

from ratings.models import Survey
from ratings.forms import NewSurveyForm


class SurveyList(ListView):
    model = Survey


class NewSurveyView(CreateView):
    template_name = 'ratings/new_survey.html'
    form_class = NewSurveyForm
    success_url = reverse_lazy('survey_list')
