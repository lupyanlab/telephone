import pydub

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Game, Message


class NewGameForm(forms.ModelForm):
    num_chains = forms.IntegerField(initial=1, min_value=1)

    class Meta:
        model = Game
        fields = ('name', )

    def __init__(self, *args, **kwargs):
        super(NewGameForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'new_game'
        self.helper.add_input(Submit('submit', 'Create'))

    def save(self, *args, **kwargs):
        game = super(NewGameForm, self).save(*args, **kwargs)

        for i in range(self.cleaned_data['num_chains']):
            chain = game.chain_set.create()
            chain.message_set.create()

        return game


class TrimMessageForm(forms.Form):
    message = forms.ModelChoiceField(queryset=Message.objects.all())
    start = forms.FloatField()
    end = forms.FloatField()

    def trim(self):
        message = self.cleaned_data['message']
        start_msec = self.cleaned_data['start'] * 1000
        end_msec = self.cleaned_data['end'] * 1000

        audio_segment = pydub.AudioSegment.from_wav(message.audio.path)
        trimmed_segment = audio_segment[start_msec:end_msec]
        trimmed_segment.export(message.audio.path, format='wav')
        return message
