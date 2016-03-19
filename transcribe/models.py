import logging

from django.db import models

from grunt.models import Message
from transcribe.exceptions import *


class TranscriptionSurvey(models.Model):
    name = models.CharField(max_length=100)
    num_transcriptions_per_taker = models.IntegerField(default=10)
    catch_trial_id = models.IntegerField(blank=True, null=True)

    def pick_next_message(self, receipts=None):
        """Randomly select the next message to transcribe for this user.

        If this survey has a catch trial, make sure the user completes it.

        Args:
            receipts (list): The messages this user has already answered.
        Returns:
            Transcription
        """
        receipts = receipts or []

        # Receipts are transcription ids so they can be used to
        # create a unique completion code. Here we go backward
        # from the transcriptions to the messages they were a
        # transcription of. There are many more transcriptions
        # than there are messages.
        completed_messages = Transcription.objects.\
            filter(id__in=receipts).\
            values_list('message', flat=True)

        if len(receipts) == self.num_transcriptions_per_taker - 1:
            # If there is a catch trial and they haven't taken it yet,
            # give it to them as the last question.
            if self.catch_trial_id and self.catch_trial_id not in completed_messages:
                return self.messages.get(pk=self.catch_trial_id)
        elif len(receipts) == self.num_transcriptions_per_taker:
            raise SurveyCompleteException()
        elif len(receipts) > self.num_transcriptions_per_taker:
            msg = 'user had {} receipts when survey requested {}'
            args = (len(receipts), self.num_transcriptions_per_taker)
            logging.error(msg.format(*args))
            raise SurveyCompleteException()

        try:
            selected_message = self.messages.\
                exclude(id__in=completed_messages).\
                order_by('?')[0]
        except IndexError:
            raise NoMoreMessagesException()
        else:
            return selected_message

    def __str__(self):
        return '{}: {}'.format(self.pk, self.name)


class MessageToTranscribe(models.Model):
    survey = models.ForeignKey(TranscriptionSurvey, related_name='messages')
    given = models.ForeignKey(Message, related_name='transcribe_questions')


class Transcription(models.Model):
    message = models.ForeignKey(MessageToTranscribe,
                                related_name='transcribed_messages')
    text = models.CharField(max_length=60)
