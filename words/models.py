import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models

from grunt.models import Message


class Survey(models.Model):
    name = models.CharField(max_length=30, unique=True)
    num_questions_per_player = models.IntegerField(default=10)

    def pick_next_question(self, receipts=[]):
        if len(receipts) >= self.num_questions_per_player:
            raise Question.DoesNotExist('No questions left to take')

        completed_questions = (Response.objects
                                       .filter(id__in=receipts)
                                       .values_list('question', flat=True))
        try:
            return (self.questions
                        .exclude(id__in=completed_questions)
                        .order_by('?')[0])
        except IndexError:
            raise Question.DoesNotExist('No questions left to take')

    def __str__(self):
        return self.name


class Question(models.Model):
    survey = models.ForeignKey(Survey, related_name='questions')
    word = models.CharField(max_length=60)
    choices = models.ManyToManyField(Message, related_name='word_questions')


class Response(models.Model):
    question = models.ForeignKey(Question, related_name='responses')
    selection = models.ForeignKey(Message, related_name='word_responses')
