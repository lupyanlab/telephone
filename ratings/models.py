from django.db import models

from grunt.models import Message


class Survey(models.Model):
    pass


class Question(models.Model):
    survey = models.ForeignKey(Survey, related_name='questions')
    given = models.OneToOneField(Message, related_name='given')
    choices = models.ManyToManyField(Message)
    answer = models.OneToOneField(Message, related_name='answer',
                                  null=True, blank=True)
    selection = models.OneToOneField(Message, related_name='selection',
                                     null=True, blank=True)
