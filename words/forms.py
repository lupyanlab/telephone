from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from ratings.forms import MessageIdField
from words.models import Survey, Question


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
    choices = MessageIdField()

    class Meta:
        model = Question
        fields = ('survey', 'word', 'choices')
