
from django.test import TestCase

from model_mommy import mommy

from grunt.models import Message
from ratings.models import Survey, Question, Response


class SurveyModelTest(TestCase):
    def setUp(self):
        super(SurveyModelTest, self).setUp()
        self.survey = mommy.make(Survey)
        self.questions = [self.make_question(survey=self.survey)] * 5

    def make_question(self, **mommy_kwargs):
        recording = mommy.make_recipe('ratings.recording')
        return mommy.make_recipe('ratings.question', given=recording,
                                 **mommy_kwargs)

    def test_create_new_survey(self):
        survey = Survey(name='New Survey 1')
        survey.full_clean()  # should not raise

    def test_pick_next_question(self):
        next_question = self.survey.pick_next_question()
        self.assertIsInstance(next_question, Question)

    def test_pick_next_question_raises_when_all_are_completed(self):
        receipts = []
        for q in self.questions:
            response = mommy.make_recipe('ratings.response', question=q)
            receipts.append(response.pk)

        with self.assertRaises(Question.DoesNotExist):
            self.survey.pick_next_question(receipts)


class QuestionModelTest(TestCase):
    def test_create_new_question(self):
        """Add a question to a survey requires two recordings."""
        survey = mommy.make(Survey)
        given, answer = mommy.make_recipe('ratings.recording', _quantity=2)
        question = Question(survey=survey, given=given, answer=answer)
        question.full_clean()
        question.save()  # should not raise

    def test_add_choices_to_question(self):
        """Add choices to an empty question."""
        num_choices = 3
        question = mommy.make_recipe('ratings.empty_question')
        messages = mommy.make_recipe('ratings.seed', _quantity=num_choices)
        question.choices.add(*messages)
        self.assertEquals(question.choices.count(), num_choices)

    def test_add_same_choices_to_multiple_questions(self):
        num_choices = 3
        question1, question2 = mommy.make_recipe('ratings.empty_question',
                                                 _quantity=2)
        messages = mommy.make_recipe('ratings.recording', _quantity=num_choices)
        question1.choices.add(*messages)
        question2.choices.add(*messages)
        self.assertEquals(question1.choices.count(), num_choices)
        self.assertEquals(question2.choices.count(), num_choices)


class ResponseModelTest(TestCase):
    def test_submit_a_response(self):
        question = mommy.make(Question)
        selection = mommy.make(Message)
        response = Response(question=question, selection=selection)
        response.full_clean()
        response.save()  # should not raise

    def test_allow_multiple_responses_per_question(self):
        question = mommy.make(Question)
        selection = mommy.make(Message)
        response_1 = mommy.make(Response, question=question,
                                selection=selection)
        response_2 = mommy.make(Response, question=question,
                                selection=selection)  # should not raise

        self.assertEquals(Response.objects.count(), 2)
