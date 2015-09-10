from django.views.generic import ListView

from ratings.models import Survey


class SurveyList(ListView):
    model = Survey
