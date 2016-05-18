from django.views.generic import ListView, CreateView
from django.core.urlresolvers import reverse_lazy

from words.models import Survey
from words.forms import NewWordSurveyForm

class WordSurveyList(ListView):
    model = Survey
    queryset = Survey.objects.all().order_by('-id')
    template_name = 'words/survey_list.html'


class NewSurveyView(CreateView):
    template_name = 'words/new_survey.html'
    form_class = NewWordSurveyForm
    success_url = reverse_lazy('words_list')
