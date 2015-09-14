from unittest import skip
from unipath import Path

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from model_mommy import mommy

from grunt.models import Message
from ratings.models import Survey, Question, Response
from ratings.forms import NewSurveyForm, ResponseForm

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

class SurveyViewTest(TestCase):
    def setUp(self):
        self.survey_list_url = reverse('survey_list')

    @skip("Test is getting run twice for some reason")
    def test_surveys_show_up_on_survey_list_page(self):
        survey = mommy.make(Survey)
        response = self.client.get(self.survey_list_url)
        surveys = response.context['survey_list']
        self.assertEquals(len(surveys), 1)

    def test_survey_list_view_renders_survey_list_template(self):
        response = self.client.get(self.survey_list_url)
        self.assertTemplateUsed(response, 'ratings/survey_list.html')

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


@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class TakeSurveyTest(SurveyViewTest):
    def setUp(self):
        super(TakeSurveyTest, self).setUp()
        self.survey = mommy.make(Survey)
        self.question = mommy.make(Question, survey=self.survey)
        self.question.choices.add(mommy.make(Message, _fill_optional='audio'))

    def tearDown(self):
        super(TakeSurveyTest, self).tearDown()
        TEST_MEDIA_ROOT.rmtree()

    def add_question_to_session(self):
        response = mommy.make(Response, question=self.question)

        self.client.get(self.survey.get_survey_url())
        session = self.client.session
        session['completed_questions'] = [self.question.pk, ]
        session['receipts'] = [response.pk, ]
        session.save()

    def test_taking_a_survey_renders_the_question_template(self):
        response = self.client.get(self.survey.get_survey_url())
        self.assertTemplateUsed(response, 'ratings/question.html')

    def test_taking_a_survey_renders_the_question_obj(self):
        response = self.client.get(self.survey.get_survey_url())
        self.assertIsInstance(response.context['question'], Question)

    def test_taking_a_survey_renders_the_question_form(self):
        response = self.client.get(self.survey.get_survey_url())
        self.assertIsInstance(response.context['form'], ResponseForm)

    def test_post_a_response(self):
        post_data = {'question': self.question.pk,
                     'selection': self.question.choices.first().pk}
        self.client.post(self.survey.get_survey_url(), post_data)

    def test_completed_survey_takers_get_the_completion_page(self):
        self.add_question_to_session()
        response = self.client.get(self.survey.get_survey_url())
        self.assertTemplateUsed(response, 'ratings/complete.html')
