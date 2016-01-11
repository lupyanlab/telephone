from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.models import Message, Chain
from ratings.models import Survey
from ratings.forms import NewSurveyForm, CreateQuestionForm

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class RatingsModelTest(TestCase):
    def tearDown(self):
        super(RatingsModelTest, self).tearDown()
        TEST_MEDIA_ROOT.rmtree()


class NewSurveyFormTest(RatingsModelTest):
    def create_choice_and_question_message_ids(self):
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

        extract_ids = lambda msg_list: [str(msg.id) for msg in msg_list]
        question_ids = extract_ids(questions)
        choice_ids = extract_ids(choices)
        return question_ids, choice_ids

    def test_make_new_survey(self):
        question_ids, choice_ids = self.create_choice_and_question_message_ids()

        questions_str = ','.join(question_ids)
        choices_str = ','.join(choice_ids)

        survey_form = NewSurveyForm({
            'name': 'Test Survey',
            'num_questions_per_player': 4,
            'questions': questions_str,
            'choices': choices_str,
        })

        self.assertTrue(survey_form.is_valid())
        survey = survey_form.save()  # should not raise
        self.assertEquals(Survey.objects.count(), 1)

        self.assertEquals(survey.questions.count(), 4)

    def test_questions_can_contain_spaces(self):
        question_ids, choice_ids = self.create_choice_and_question_message_ids()

        questions_str = ', '.join(question_ids)
        choices_str = ', '.join(choice_ids)

        survey_form = NewSurveyForm({
            'name': 'Spaced Survey',
            'num_questions_per_player': 4,
            'questions': questions_str,
            'choices': choices_str,
        })
        self.assertTrue(survey_form.is_valid())

    def test_questions_must_be_actual_messages(self):
        questions_str = '1,2,3'
        choices_str = '4,5,6'
        survey_form = NewSurveyForm({
            'name': 'Bad Survey',
            'num_questions_per_player': 4,
            'questions': questions_str,
            'choices': choices_str,
        })
        self.assertFalse(survey_form.is_valid())

    def test_questions_must_be_csv_ints(self):
        questions_str = 'a,b,c'
        choices_str = 'd,e,f'
        survey_form = NewSurveyForm({
            'name': 'Str Message Survey',
            'num_questions_per_player': 4,
            'questions': questions_str,
            'choices': choices_str,
        })
        self.assertFalse(survey_form.is_valid())


class CreateQuestionFormTest(RatingsModelTest):
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
            'choices': [message.id for message in choices],
            'determine_correct_answer': True,
        }
        question_form = CreateQuestionForm(question_data)
        self.assertTrue(question_form.is_valid())

        question = question_form.save()
        self.assertEquals(list(question.choices.all()), choices)
        self.assertEquals(question.answer, seed)
        self.assertEquals(survey.questions.count(), 1)

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
            'choices': [message.id for message in choices],
            'determine_correct_answer': True,
        }
        question_form = CreateQuestionForm(question_data)
        with self.assertRaises(Message.DoesNotExist):
            question_form.save()

    def test_delete_question_if_answer_not_found_in_choices(self):
        chain1, chain2 = mommy.make(Chain, _quantity=2)
        seed = mommy.make(Message, chain=chain1)
        other_seed = mommy.make(Message, chain=chain2)

        gen1 = mommy.make(Message, parent=seed, chain=chain1)

        survey = mommy.make(Survey)
        self.assertEquals(survey.questions.count(), 0)

        choices = [other_seed, ]
        question_data = {
            'survey': survey.id,
            'given': gen1.id,
            'choices': [message.id for message in choices],
            'determine_correct_answer': True,
        }
        question_form = CreateQuestionForm(question_data)
        with self.assertRaises(Message.DoesNotExist):
            question_form.save()

        self.assertEquals(survey.questions.count(), 0)
