from django.db import models

from .handlers import message_file_name


class Game(models.Model):
    """ Top-level control over chains. """
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Chain(models.Model):
    """ Strings of messages. """
    game = models.ForeignKey(Game, related_name='chains')
    name = models.CharField(max_length=30)
    seed = models.FileField(upload_to='seeds/')

    def __str__(self):
        return '{} - {}'.format(self.game, self.name)


class Message(models.Model):
    """ Audio recording of a vocal imitation. """
    chain = models.ForeignKey(Chain, blank=True, null=True,
                              related_name='messages')
    parent = models.ForeignKey('self', blank=True, null=True)
    generation = models.IntegerField(default=0, editable=False)
    audio = models.FileField(upload_to=message_file_name)
    alive = models.BooleanField(default=True)

    def kill(self):
        self.alive = False
        self.save()
