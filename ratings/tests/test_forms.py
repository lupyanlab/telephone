
from django.core.exceptions import ValidationError
from django.test import TestCase

from model_mommy import mommy

from grunt.models import Message, Chain
from ratings.models import Survey
from ratings.forms import SurveyForm, CreateQuestionForm


class SurveyFormTest(TestCase):
    def test_make_new_survey(self):
        chains = mommy.make(Chain, _quantity=4)

        choices = []
        for chain in chains:
            seed_message = mommy.make(Message, chain=chain)
            choices.append(seed_message)

        questions = []
        for seed_message in choices:
            response = mommy.make(Message, chain=seed_message.chain,
                                  parent=seed_message)
            questions.append(response)

        choices_str = ','.join([str(message.id) for message in choices])
        questions_str = ','.join([str(message.id) for message in questions])

        survey_form = SurveyForm({'questions': questions_str,
                                  'choices': choices_str})
        self.assertTrue(survey_form.is_valid())
        survey = survey_form.save()  # should not raise
        self.assertEquals(Survey.objects.count(), 1)

        self.assertEquals(survey.questions.count(), 4)

    def test_questions_must_be_actual_messages(self):
        questions_str = '1,2,3'
        choices_str = '4,5,6'
        survey_form = SurveyForm({'questions': questions_str,
                                  'choices': choices_str})
        self.assertFalse(survey_form.is_valid())

    def test_questions_must_be_csv_ints(self):
        questions_str = 'a,b,c'
        choices_str = 'd,e,f'
        survey_form = SurveyForm({'questions': questions_str,
                                  'choices': choices_str})
        self.assertFalse(survey_form.is_valid())

    def test_questions_can_contain_spaces(self):
        questions = mommy.make(Message, _quantity=10)
        questions_str = ', '.join([str(message.id) for message in questions])

        choices = mommy.make(Message, _quantity=4)
        choices_str = ',  '.join([str(message.id) for message in choices])

        survey_form = SurveyForm({'questions': questions_str,
                                  'choices': choices_str})
        self.assertTrue(survey_form.is_valid())


class CreateQuestionFormTest(TestCase):
    def test_select_answer_from_choices(self):
        chain1, chain2 = mommy.make(Chain, _quantity=2)
        seed = mommy.make(Message, chain=chain1)
        other_seed = mommy.make(Message, chain=chain2)

        gen1 = mommy.make(Message, parent=seed, chain=chain1)

        survey = mommy.make(Survey)
        choices = [seed, other_seed]
        question_data = {
            'survey': survey.id,
            'given': gen1.id,
            'choices': [message.id for message in choices]
        }
        question_form = CreateQuestionForm(question_data)
        self.assertTrue(question_form.is_valid())

        question = question_form.save()
        self.assertEquals(list(question.choices.all()), choices)
        self.assertEquals(question.answer, seed)

    def test_validation_error_if_no_choice_in_given_chain(self):
        chain1, chain2 = mommy.make(Chain, _quantity=2)
        seed = mommy.make(Message, chain=chain1)
        other_seed = mommy.make(Message, chain=chain2)

        gen1 = mommy.make(Message, parent=seed, chain=chain1)

        survey = mommy.make(Survey)
        choices = [other_seed, ]
        question_data = {
            'survey': survey.id,
            'given': gen1.id,
            'choices': [message.id for message in choices]
        }
        question_form = CreateQuestionForm(question_data)
        with self.assertRaises(ValidationError):
            question_form.save()
