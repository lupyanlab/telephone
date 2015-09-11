from django.core.urlresolvers import reverse
from django.db import models

from grunt.models import Message


class Survey(models.Model):
    name = models.CharField(max_length=30)

    def get_inspect_url(self):
        return reverse('inspect_survey', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

class Question(models.Model):
    survey = models.ForeignKey(Survey, related_name='questions')
    given = models.OneToOneField(Message, related_name='given')
    choices = models.ManyToManyField(Message)
    answer = models.OneToOneField(Message, related_name='answer',
                                  null=True, blank=True)
    selection = models.OneToOneField(Message, related_name='selection',
                                     null=True, blank=True)
