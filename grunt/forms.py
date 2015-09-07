
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Game


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
