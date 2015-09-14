from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

from grunt.models import Message
from ratings.models import Survey, Question, Response


class MessageIdField(forms.Field):
    def to_python(self, value):
        try:
            return map(int, value.split(','))
        except AttributeError:
            # value is already a list, so just make sure they are ints
            return map(int, value)
        except ValueError:
            raise ValidationError('Messages must be given as ints')

    def validate(self, value):
        all_message_ids = Message.objects.values_list('id', flat=True)
        for message_id in value:
            if message_id not in all_message_ids:
                raise ValidationError('Message not found')


class NewSurveyForm(forms.ModelForm):
    questions = MessageIdField()
    choices = MessageIdField()

    class Meta:
        model = Survey
        fields = ('name', 'questions', 'choices')

    def __init__(self, *args, **kwargs):
        super(NewSurveyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create'))

    def save(self):
        """ Create a survey and then create questions for that survey """
        survey = super(NewSurveyForm, self).save()

        choices = self.cleaned_data['choices']
        for message_id in self.cleaned_data.get('questions'):
            question_data = {
                'survey': survey.id,
                'given': message_id,
                'choices': choices,
            }
            question_form = CreateQuestionForm(question_data)
            if question_form.is_valid():
                question_form.save()

        return survey


class CreateQuestionForm(forms.ModelForm):
    choices = MessageIdField()

    class Meta:
        model = Question
        fields = ('survey', 'given', 'choices')

    def save(self):
        question = super(CreateQuestionForm, self).save()
        if not question.answer:
            try:
                choices = question.choices.all()
                question.answer = question.given.find_ancestor(choices)
            except Message.DoesNotExist, e:
                question.delete()
                raise e
        return question

class ResponseForm(forms.ModelForm):

    class Meta:
        model = Response
        fields = ('question', 'selection')

    def __init__(self, *args, **kwargs):
        super(ResponseForm, self).__init__(*args, **kwargs)

        self.fields['selection'].required = True

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('question', type='hidden'),
            InlineRadios('selection'),
            Submit('submit', 'Submit')
        )
