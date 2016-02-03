from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Message, Game, Chain


class ResponseForm(forms.ModelForm):
    """Save the message received from the player."""
    class Meta:
        model = Message
        fields = ('parent', 'audio')

    def save(self, **kwargs):
        """Create a new message and populate fields from parent."""
        message = super(ResponseForm, self).save(**kwargs)
        message.chain = message.parent.chain
        message.generation = message.parent.generation + 1
        message.save()
        return message


class NewGameForm(forms.ModelForm):
    """Create a new game.

    ModelForm fields:
        name: The name of the game.

    Additional fields:
        num_chains: The number of chains in this game. Used by the view to
            render the correct number of new chain forms on the following page.
        num_seeds_per_chain: The number of seed audio files that will be
            uploaded for each chain.
    """
    num_chains = forms.IntegerField(initial=1, min_value=1)
    num_seeds_per_chain = forms.IntegerField(initial=1, min_value=1)

    class Meta:
        model = Game
        fields = ('name', )

    def __init__(self, *args, **kwargs):
        """Crispy form."""
        super(NewGameForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create'))


class NewChainForm(forms.ModelForm):
    """A form for creating new chains populated with seed messages.

    Form FileFields are added dynamically on form creation to allow for
    building chains with muliple seed messages.

    Attributes:
        NUM_SEEDS: An int specifying the number of seeds to expect. This
            is useful as a class attribute because it can be set prior to
            using this form in a model formset view that allows for creating
            multiple chains (with multiple seeds) on the same page.
    """
    NUM_SEEDS = 1

    class Meta:
        model = Chain
        fields = ('game', 'name')
        widgets = {'game': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        """Create the form and dynamically add FileFields for seed messages."""
        super(NewChainForm, self).__init__(*args, **kwargs)

        # save the field names to the form object for later use
        self.seed_fields = ['seed{}'.format(ix) for ix in range(self.NUM_SEEDS)]

        for seed_field_name in self.seed_fields:
            self.fields[seed_field_name] = forms.FileField()

    def save(self, **kwargs):
        """Create a new chain and then create seed messages for it."""
        chain = super(NewChainForm, self).save(**kwargs)

        # create multiple seed messages for this chain
        for seed_field_name in self.seed_fields:
            chain.messages.create(
                audio=self.cleaned_data[seed_field_name],
                # if was uploaded it's probably good
                edited=True,
            )

        return chain


class NewChainFormSet(forms.models.BaseModelFormSet):
    pass


class NewChainFormSetHelper(FormHelper):
    """Styling specific to pages rendering multiple new chain forms.

    Although the page will have multiple NewChainForms, it should only
    have a single submit button, which Crispy can create for us.
    """
    def __init__(self, *args, **kwargs):
        super(NewChainFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.add_input(Submit('submit', 'Create'))
