from unipath import Path

from django.conf import settings
from django.test import TestCase, override_settings

from model_mommy import mommy

from grunt.models import Message
from ratings.models import Survey, Question, Choice

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class SurveyTest(TestCase):
    def tearDown(self):
        super(SurveyTest, self).tearDown()
        TEST_MEDIA_ROOT.rmtree()

    def test_create_new_survey(self):
        survey = Survey()
        survey.full_clean()  # should not raise

    def test_create_new_question(self):
        survey = mommy.make(Survey)
        given = mommy.make(Message)
        answer = mommy.make(Message)
        question = Question(survey=survey, given=given, answer=answer)
        question.full_clean()  # should not raise

    def test_add_choices_to_question(self):
        num_choices = 3
        question = mommy.make(Question)
        mommy.make(Choice, question=question, _quantity=num_choices)
        self.assertEquals(question.choices.count(), num_choices)
