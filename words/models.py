import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models

from grunt.models import Message


class Survey(models.Model):
    name = models.CharField(max_length=30, unique=True)
    num_questions_per_player = models.IntegerField(default=10)
    catch_trial_id = models.IntegerField(blank=True, null=True)

    def pick_next_question(self, receipts=None):
        receipts = receipts or []
        completed_questions = (Response.objects
                                       .filter(id__in=receipts)
                                       .values_list('question', flat=True))

        if len(receipts) == self.num_questions_per_player-1:
            # If there is a catch trial and they haven't taken it yet,
            # give it to them as the last question.
            if self.catch_trial_id and self.catch_trial_id not in completed_questions:
                return self.questions.get(pk=self.catch_trial_id)
        elif len(receipts) >= self.num_questions_per_player:
            raise Question.DoesNotExist('No questions left to take')

        try:
            return (self.questions
                        .exclude(id__in=completed_questions)
                        .order_by('?')[0])
        except IndexError:
            raise Question.DoesNotExist('No questions left to take')

    def __str__(self):
        return '{}: {}'.format(self.pk, self.name)


class Question(models.Model):
    survey = models.ForeignKey(Survey, related_name='questions')
    word = models.CharField(max_length=60)
    choices = models.ManyToManyField(Message, related_name='word_questions')


class Response(models.Model):
    question = models.ForeignKey(Question, related_name='responses')
    selection = models.ForeignKey(Message, related_name='word_responses')
