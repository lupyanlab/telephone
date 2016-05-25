import string

from django import forms

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
    words = WordListField()
    choices = MessageIdField()

    class Meta:
        model = Survey
        fields = ('name', 'num_questions_per_player', 'words', 'choices')

    def __init__(self, *args, **kwargs):
        super(NewWordSurveyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create'))

    def save(self):
        """Create a survey and then create questions for that survey."""
        survey = super(NewWordSurveyForm, self).save()

        choices = self.cleaned_data['choices']
        for word in self.cleaned_data.get('words'):
            question_data = {
                'survey': survey.id,
                'word': word,
                'choices': choices,
            }

            question_form = NewWordQuestionForm(question_data)
            question_form.save()

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
