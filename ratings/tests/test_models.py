
from django.test import TestCase

from model_mommy import mommy

from grunt.models import Message
from ratings.models import Survey, Question


class SurveyModelTest(TestCase):
    def test_create_new_survey(self):
        survey = Survey(name='New Survey 1')
        survey.full_clean()  # should not raise


class QuestionModelTest(TestCase):
    def test_create_new_question(self):
        survey = mommy.make(Survey)
        given = mommy.make(Message)
        answer = mommy.make(Message)
        question = Question(survey=survey, given=given, answer=answer)
        question.full_clean()  # should not raise

    def test_add_choices_to_question(self):
        num_choices = 3
        question = mommy.make(Question)
        messages = mommy.make(Message, _quantity=num_choices)
        question.choices.add(*messages)
        self.assertEquals(question.choices.count(), num_choices)

    def test_add_same_choices_to_multiple_questions(self):
        num_choices = 3
        question1, question2 = mommy.make(Question, _quantity=2)
        messages = mommy.make(Message, _quantity=num_choices)
        question1.choices.add(*messages)
        question2.choices.add(*messages)
        self.assertEquals(question1.choices.count(), num_choices)
        self.assertEquals(question2.choices.count(), num_choices)
