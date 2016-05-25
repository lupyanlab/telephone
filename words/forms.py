import string

from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

from ratings.forms import MessageIdField
from words.models import Survey, Question, Response


class WordListField(forms.Field):
    """Splits a comma separated list into a python list."""
    def to_python(self, value):
        if value is None and not self.required:
            return ''

        try:
            return value.split(',')
        except AttributeError:
            # value is already a list, so just make sure they are strings
            return map(str, value)
        except ValueError:
            raise ValidationError('Messages must be given as strings')


class NewWordSurveyForm(forms.ModelForm):
    """Create a new survey to obtain match to seed ratings from words."""
    words = WordListField(required=False)
    words_file = forms.FileField(required=False)
    choices = MessageIdField()
    catch_trial = forms.CharField(required=False)

    class Meta:
        model = Survey
        fields = ('name', 'num_questions_per_player')

    def __init__(self, *args, **kwargs):
        super(NewWordSurveyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create'))

    def clean(self):
        super(NewWordSurveyForm, self).clean()
        if not (self.cleaned_data['words'] or self.data['words_file']):
            raise ValidationError('either words or words_file must be given')

    def save(self):
        """Create a survey and then create questions for that survey."""
        survey = super(NewWordSurveyForm, self).save()

        choices = self.cleaned_data['choices']

        words = self.cleaned_data.get('words')
        if not words or words == [u'']:
            # !!! Watch out for words being a list of an empty string
            words = words_from_file(self.cleaned_data['words_file'])

        for word in words:
            question_data = {
                'survey': survey.id,
                'word': word,
                'choices': choices,
            }

            question_form = NewWordQuestionForm(question_data)
            question_form.save()

        catch_trial = self.cleaned_data.get('catch_trial')
        if catch_trial:
            catch_trial_data = {
                'survey': survey.id,
                'word': catch_trial,
                'choices': choices,
            }
            question_form = NewWordQuestionForm(catch_trial_data)
            catch_question = question_form.save()
            survey.catch_trial_id = catch_question.pk
            survey.save()

        return survey


class NewWordQuestionForm(forms.ModelForm):
    """Simple ModelForm around questions for word surveys."""
    choices = MessageIdField()

    class Meta:
        model = Question
        fields = ('survey', 'word', 'choices')


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ('question', 'selection')
        error_messages = {
            'selection': {
                'required': 'You must select one of the choices.',
            },
        }

    def __init__(self, *args, **kwargs):
        super(ResponseForm, self).__init__(*args, **kwargs)

        self.fields['selection'].required = True
        self.fields['selection'].empty_label = None
        self.fields['selection'].label = ''

        if 'question' in self.initial:
            message_choices = self.initial['question'].choices.all()
            self.fields['selection'].queryset = message_choices
            choice_labels = list(string.letters[:len(message_choices)])
            choice_map = [(message.id, label) for message, label in zip(message_choices, choice_labels)]
            self.fields['selection'].widget.choices = choice_map

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('question', type='hidden'),
            InlineRadios('selection'),
            Submit('submit', 'Submit')
        )


def words_from_file(django_file):
    return django_file.read().splitlines()
