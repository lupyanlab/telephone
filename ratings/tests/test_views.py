from unittest import skip
from unipath import Path

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.utils.six import BytesIO

from model_mommy import mommy
from rest_framework.parsers import JSONParser

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
        givens = mommy.make(Message, _fill_optional=['chain'], _quantity=num_questions)
        for g in givens:
            mommy.make(Question, survey=survey, given=g)
        response = self.client.get(reverse('inspect_survey', kwargs={'pk':survey.pk}))
        questions = response.context['questions']
        self.assertEquals(len(questions), num_questions)


@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class TakeSurveyTest(SurveyViewTest):
    def setUp(self):
        super(TakeSurveyTest, self).setUp()
        self.survey = mommy.make(Survey)
        given, choice = mommy.make(Message, _fill_optional=['chain', 'audio'], _quantity=2)
        self.question = mommy.make(Question, given=given, survey=self.survey)
        self.question.choices.add(choice)

        self.survey_url = reverse('take_survey', kwargs={'pk': self.survey.pk})

    def tearDown(self):
        super(TakeSurveyTest, self).tearDown()
        TEST_MEDIA_ROOT.rmtree()

    def add_question_to_session(self):
        selection = mommy.make(Message, _fill_optional=['chain', 'audio'])
        response = mommy.make(Response, question=self.question, selection=selection)

        self.client.get(self.survey_url)
        session = self.client.session
        session['receipts'] = [response.pk, ]
        session.save()

    def test_taking_a_survey_renders_the_question_template(self):
        response = self.client.get(self.survey_url)
        self.assertTemplateUsed(response, 'ratings/question.html')

    def test_taking_a_survey_renders_the_question_as_json(self):
        response = self.client.get(self.survey_url)
        stream = BytesIO(response.context['question'])
        question_data = JSONParser().parse(stream)
        self.assertIn('audio', question_data)

    def test_taking_a_survey_renders_the_question_form(self):
        response = self.client.get(self.survey_url)
        self.assertIsInstance(response.context['form'], ResponseForm)

    def test_post_a_response(self):
        self.client.get(self.survey_url)  # populates session
        post_data = {'question': self.question.pk,
                     'selection': self.question.choices.first().pk}
        self.client.post(self.survey_url, post_data)

    def test_completed_players_get_the_completion_page(self):
        self.add_question_to_session()
        response = self.client.get(self.survey_url)
        self.assertTemplateUsed(response, 'ratings/complete.html')

    def test_completed_players_get_their_sessions_cleared(self):
        self.add_question_to_session()
        completed = self.client.session['receipts']
        self.assertIsNotNone(completed)
        response = self.client.get(self.survey_url)
        self.assertTemplateUsed(response, 'ratings/complete.html')
        completed = self.client.session['receipts']
        self.assertEquals(len(completed), 0)
