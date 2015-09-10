from django import forms
from django.core.exceptions import ValidationError

from grunt.models import Message


class SurveyForm(forms.Form):
    # message pks, comma-separated
    # A rating will be created for each message
    questions = forms.CharField()

    # message pks, comma-separated
    # All choices are present for every rating
    choices = forms.CharField()

    def clean_questions(self):
        self.verify_message_str(self.cleaned_data.get('questions'))

    def clean_choices(self):
        self.verify_message_str(self.cleaned_data.get('choices'))

    def verify_message_str(self, message_str):
        message_ids = map(int, message_str.split(','))
        all_message_ids = Message.objects.values_list('id', flat=True)
        for message_id in message_ids:
            if message_id not in all_message_ids:
                raise ValidationError('Message not found')
