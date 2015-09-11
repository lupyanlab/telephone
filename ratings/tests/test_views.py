from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from ratings.models import Survey, Question
from ratings.forms import NewSurveyForm


class ViewTest(TestCase):
    survey_list_url = reverse('survey_list')

    def test_survey_list_view_renders_survey_list_template(self):
        response = self.client.get(self.survey_list_url)
        self.assertTemplateUsed(response, 'ratings/survey_list.html')

    def test_surveys_show_up_on_survey_list_page(self):
        num_surveys = 10
        expected_surveys = mommy.make(Survey, _quantity=num_surveys)
        response = self.client.get(self.survey_list_url)
        surveys = response.context['survey_list']
        self.assertEquals(len(surveys), num_surveys)

    def test_new_survey_view_renders_new_survey_form(self):
        new_survey_url = reverse('new_survey')
        response = self.client.get(new_survey_url)
        form = response.context['form']
        self.assertIsInstance(form, NewSurveyForm)

    def test_questions_show_up_on_survey_view_page(self):
        num_questions = 10
        survey = mommy.make(Survey)
        mommy.make(Question, survey=survey, _quantity=num_questions)
        response = self.client.get(survey.get_inspect_url())
        questions = response.context['questions']
        self.assertEquals(len(questions), num_questions)
