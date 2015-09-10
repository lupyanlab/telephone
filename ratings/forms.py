from django import forms
from django.core.exceptions import ValidationError

from grunt.models import Message


class MessageIdField(forms.Field):
    def to_python(self, value):
        try:
            return map(int, value.split(','))
        except ValueError:
            raise ValidationError('Messages must be given as ints')

    def validate(self, value):
        all_message_ids = Message.objects.values_list('id', flat=True)
        for message_id in value:
            if message_id not in all_message_ids:
                raise ValidationError('Message not found')


class SurveyForm(forms.Form):
    # message pks, comma-separated
    # A rating will be created for each message
    questions = MessageIdField()

    # message pks, comma-separated
    # All choices are present for every rating
    choices = MessageIdField()
