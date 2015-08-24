
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
