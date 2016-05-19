import unipath

from django.conf import settings
from django.test import TestCase, override_settings

from model_mommy import mommy

from grunt.models import Message
from words.models import Survey, Question, Response
from words.forms import NewWordSurveyForm, NewWordQuestionForm


TEST_MEDIA_ROOT = unipath.Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CreateWordSurveyTest(TestCase):
    def tearDown(self):
        super(CreateWordSurveyTest, self).tearDown()
        TEST_MEDIA_ROOT.rmtree()

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

    def test_create_word_question(self):
        survey = mommy.make(Survey)
        choices = mommy.make_recipe('ratings.seed', _quantity=4)
        data = dict(
            survey=survey.id,
            word='booba',
            choices=[message.id for message in choices],
        )
        form = NewWordQuestionForm(data)
        self.assertTrue(form.is_valid())
