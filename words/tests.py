import unipath

from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy

from grunt.models import Message
from words.models import Survey, Question, Response
from words.forms import NewWordSurveyForm, NewWordQuestionForm


TEST_MEDIA_ROOT = unipath.Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CreateWordSurveyTest(TestCase):
    def setUp(self):
        super(CreateWordSurveyTest, self).setUp()
        self.words = ['booba', 'kiki']
        self.words_str = ','.join(self.words)

        self.txt_path = unipath.Path('test-words-upload.txt').absolute()
        with open(self.txt_path, 'w') as f:
            for w in self.words:
                f.write(w+'\n')
        self.words_file = File(open(self.txt_path, 'r'))

        choices = mommy.make_recipe('ratings.seed', _quantity=4)
        self.choice_ids = [message.id for message in choices]
        self.choices_str = ','.join(map(str, self.choice_ids))

    def tearDown(self):
        super(CreateWordSurveyTest, self).tearDown()
        TEST_MEDIA_ROOT.rmtree()
        if self.txt_path.exists():
            self.txt_path.remove()

    def test_create_word_survey(self):
        form_data = dict(
            name='word survey 1',
            num_questions_per_player=2,
            words=self.words_str,
            choices=self.choices_str,
        )

        form = NewWordSurveyForm(form_data)
        self.assertTrue(form.is_valid())

        survey = form.save()
        self.assertEqual(survey.questions.count(), 2)

    def test_create_word_survey_from_file(self):
        form_data = dict(
            name='word survey 1',
            num_questions_per_player=2,
            words_file=self.words_file,
            choices=self.choices_str,
        )

        form = NewWordSurveyForm(form_data)
        self.assertTrue(form.is_valid(), form.errors)

        survey = form.save()
        self.assertEqual(survey.questions.count(), 2)

    def test_word_survey_requires_one_of_words(self):
        form_data = dict(
            name='word survey 1',
            num_questions_per_player=2,
            choices=self.choices_str,
        )
        form = NewWordSurveyForm(form_data)
        self.assertFalse(form.is_valid())

    def test_create_word_question(self):
        survey = mommy.make(Survey)
        data = dict(
            survey=survey.id,
            word='booba',
            choices=self.choice_ids,
        )
        form = NewWordQuestionForm(data)
        self.assertTrue(form.is_valid())


    def test_pick_next_question(self):
        survey = mommy.make(Survey)
        question = mommy.make(Question, survey=survey)
        received = survey.pick_next_question()
        self.assertEquals(question, received)
