import pydub

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from grunt.models import Message


class UploadMessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('audio', )

    def __init__(self, *args, **kwargs):
        super(UploadMessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Upload'))

    def save(self, *args, **kwargs):
        message = super(UploadMessageForm, self).save(*args, **kwargs)
        message.replicate()
        return message


class TrimMessageForm(forms.Form):
    message = forms.ModelChoiceField(queryset=Message.objects.all())
    start = forms.FloatField()
    end = forms.FloatField()

    def clean(self):
        cleaned_data = super(TrimMessageForm, self).clean()
        start = cleaned_data['start']
        end = cleaned_data['end']

        if start >= end:
            raise forms.ValidationError('Trim start is not before trim end')

    def trim(self):
        message = self.cleaned_data['message']
        start_msec = self.cleaned_data['start'] * 1000
        end_msec = self.cleaned_data['end'] * 1000

        audio_segment = pydub.AudioSegment.from_wav(message.audio.path)
        trimmed_segment = audio_segment[start_msec:end_msec]
        trimmed_segment.export(message.audio.path, format='wav')
        return message
