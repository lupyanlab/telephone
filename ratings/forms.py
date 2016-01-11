import string

from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

from grunt.models import Message
from ratings.models import Survey, Question, Response


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
        self.fields['selection'].label = 'Select the imitation most like the sound above.'

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
    determine_correct_answer = forms.BooleanField(required=False)

    class Meta:
        model = Survey
        fields = ('name', 'num_questions_per_player', 'questions', 'choices')

    def __init__(self, *args, **kwargs):
        super(NewSurveyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create'))

    def save(self):
        """ Create a survey and then create questions for that survey """
        survey = super(NewSurveyForm, self).save()

        question_options = {}
        question_options['determine_correct_answer'] =\
            self.cleaned_data.get('determine_correct_answer') or False

        choices = self.cleaned_data['choices']
        for message_id in self.cleaned_data.get('questions'):
            question_data = {
                'survey': survey.id,
                'given': message_id,
                'choices': choices,
            }

            question_data.update(question_options)

            question_form = CreateQuestionForm(question_data)
            question_form.save()

        return survey


class CreateQuestionForm(forms.ModelForm):
    choices = MessageIdField()

    # Should the form try to populate the answer field on save?
    determine_correct_answer = forms.BooleanField(required=False)

    class Meta:
        model = Question
        fields = ('survey', 'given', 'choices')

    def save(self):
        question = super(CreateQuestionForm, self).save()
        if self.cleaned_data['determine_correct_answer']:
            try:
                choices = question.choices.all()
                question.answer = question.given.find_ancestor(choices)
            except Message.DoesNotExist, e:
                question.delete()
                raise e
        return question
