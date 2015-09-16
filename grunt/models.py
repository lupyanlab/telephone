from django.db import models

from .handlers import message_file_name


class Game(models.Model):
    """ Top-level control over chains. """
    name = models.CharField(max_length=30)

    def pick_next_message(receipts):
        families = Message.objects.filter(id__in=receipts).values_list('chain', flat=True)
        chain = self.chains.exclude(id__in=families).order_by('?')[0]
        return chain.pick_parent()

    def __str__(self):
        return self.name


class Chain(models.Model):
    """ Strings of messages. """
    game = models.ForeignKey(Game, related_name='chains')
    name = models.CharField(max_length=30)

    def pick_parent(self):
        return self.messages.filter(num_children__gt=0).order_by('?')[0]

    def __str__(self):
        return '{} - {}'.format(self.game, self.name)


class Message(models.Model):
    """ Audio recording of a vocal imitation. """
    chain = models.ForeignKey(Chain, blank=True, null=True,
                              related_name='messages')
    parent = models.ForeignKey('self', blank=True, null=True)
    generation = models.IntegerField(default=0, editable=False)
    audio = models.FileField(upload_to=message_file_name)
    num_children = models.IntegerField(default=1)

    def kill(self):
        if self.num_children > 1:
            self.num_children -= 1
            self.save()

    def __str__(self):
        return '{} - {} (gen-{})'.format(self.chain, self.id, self.generation)

from rest_framework import serializers

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'audio')
