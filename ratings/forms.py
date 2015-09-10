from django import forms


class CreateRatingsForm(forms.Form):
    # message pks, comma-separated
    # A rating will be created for each message
    messages_to_rate = forms.CharField()

    # message pks, comma-separated
    # All choices are present for every rating
    choices = forms.CharField()

    def save(self):
        choices = self.cleaned_data['choices']
        for message_pk in self.cleaned_data['messages_to_rate']:
            rating = Rating(given=message_pk, choices=choices)
            rating.full_clean()
            rating.save()


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ('given', 'choices', 'match')
