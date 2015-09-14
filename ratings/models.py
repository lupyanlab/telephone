import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models

from grunt.models import Message


class Survey(models.Model):
    name = models.CharField(max_length=30)

    def pick_next_question(self, completed_questions=[]):
        """ Determine which question from the survey should be displayed next.

        Parameters
        ----------
        completed_questions: a list of questions already completed, by primary
            key.

        Returns
        -------
        a Question object, selected at random from the available options
        """
        questions = self.questions.all()
        if questions.count() == 0:
            raise Question.DoesNotExist('No questions in survey')

        unanswered_questions = questions.exclude(pk__in=completed_questions)
        if not unanswered_questions:
            raise Question.DoesNotExist('All questions were completed')

        return unanswered_questions.order_by('?')[0]

    def get_inspect_url(self):
        return reverse('inspect_survey', kwargs={'pk': self.pk})

    def get_survey_url(self):
        return reverse('take_survey', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

class Question(models.Model):
    survey = models.ForeignKey(Survey, related_name='questions')
    given = models.OneToOneField(Message, related_name='given')
    choices = models.ManyToManyField(Message)
    answer = models.OneToOneField(Message, related_name='answer', null=True)

    def choices_as_json(self):
        serialized_choices = [msg.as_dict() for msg in self.choices.all()]
        return json.dumps(serialized_choices)

class Response(models.Model):
    question = models.ForeignKey(Question, related_name = 'responses')
    selection = models.OneToOneField(Message)
