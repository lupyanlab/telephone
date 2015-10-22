import hashlib

from django.db import models

from rest_framework import serializers

from .handlers import message_file_name


class Game(models.Model):
    """ Top-level control over chains. """
    name = models.CharField(max_length=30)

    def pick_next_message(self, receipts=None):
        """ Determine which message the player should receive next.

        TODO: move this function to handlers
        """
        if not receipts:
            receipts = []
        families = Message.objects.filter(id__in=receipts).values_list(
            'chain', flat=True
        )
        chain = self.chains.exclude(id__in=families).order_by('?')[0]
        return chain.pick_parent()

    def __str__(self):
        return 'G{} {}'.format(self.id, self.name)


class Chain(models.Model):
    """ String of messages. """
    game = models.ForeignKey(Game, related_name='chains')
    name = models.CharField(max_length=30)

    def pick_parent(self):
        """ Select a fertile message at random.

        TODO: move this function to handlers
        """
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
    start_at = models.FloatField(default=0.0)
    end_at = models.FloatField(null=True)
    edited = models.BooleanField(default=False)
    num_children = models.IntegerField(default=1)

    def kill(self):
        if self.num_children > 0:
            self.num_children -= 1
            self.save()

    def find_ancestor(self, possible_ancestors):
        """ Trace lineage trying to find someone in possible_ancestors.

        TODO: move this function to handlers
        """
        if not self.parent:
            raise Message.DoesNotExist('No ancestors found in choices')
        elif self.parent in possible_ancestors:
            return self.parent
        else:
            return self.parent.find_ancestor(possible_ancestors)

    def __str__(self):
        """ An uninterpretable hash of this message.

        str(message) is used to label the choices in surveys!
        """
        return hashlib.sha224('{}-{}-{}'.format(
            self.chain.game.id, self.chain.id, self.id
        )).hexdigest()[:10]


class MessageSerializer(serializers.ModelSerializer):
    """ Represent a message in JSON. """
    class Meta:
        model = Message
        fields = ('id', 'audio')
