from django.test import TestCase

from model_mommy import mommy

from grunt.models import Message
from words.models import Survey, Word, Question, Response
from words.forms import NewWordSurveyForm

class CreateWordSurveyTest(TestCase):
    def test_create_word_survey(self):
        words_str = 'booba,kiki'
        choices = mommy.make_recipe('ratings.seed', _quantity=4)
        choices_str = ','.join([str(message.id) for message in choices])

        form_data = dict(
            name='word survey 1',
            num_questions_per_player=2,
            words=words_str,
            choices=choices_str,
        )

        form = NewWordSurveyForm(form_data)
        self.assertTrue(form.is_valid())
