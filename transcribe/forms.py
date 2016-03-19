from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

from grunt.models import Game
from ratings.forms import MessageIdField
from transcribe.models import Transcription, TranscriptionSurvey


class TranscriptionForm(forms.ModelForm):

    class Meta:
        model = Transcription
        fields = ('message', 'text')
        error_messages = {
            'text': {
                'required': 'You must enter a transcription.',
            },
        }

    def __init__(self, *args, **kwargs):
        super(TranscriptionForm, self).__init__(*args, **kwargs)
        self.fields['text'].required = True
        self.fields['text'].empty_label = None
        self.fields['text'].label = 'Write what you heard down as a word.'

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('message', type='hidden'),
            'text',
        )


class NewTranscriptionSurveyForm(forms.ModelForm):
    game = forms.ModelChoiceField(Game.objects.all(), empty_label=None)
    generation = forms.IntegerField(min_value=0, required=False)
    messages =  MessageIdField(required=False)

    class Meta:
        model = TranscriptionSurvey
        fields = ('name', 'num_transcriptions_per_taker')

    def __init__(self, *args, **kwargs):
        super(NewTranscriptionSurveyForm, self).__init__(*args, **kwargs)
        # crispy form
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create'))
        self.helper.layout = Layout(
            'name',
            'game',
            'generation',
            'num_transcriptions_per_taker'
        )

    def save(self):
        """Create a transcription survey and messages for that survey."""
        survey = super(NewTranscriptionSurveyForm, self).save()

        game = self.cleaned_data['game']  # think this is a model
        generation = self.cleaned_data['generation']
        grunt_messages = game.get_messages_by_generation(generation)

        # Create MessageToTranscribe objects for each grunt message
        for grunt_message in grunt_messages:
            survey.messages.create(given=grunt_message)

        return survey
