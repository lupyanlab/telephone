
from rest_framework import serializers

from grunt.models import Chain, Message, Game


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'parent', 'audio', 'generation', 'num_children')

class ChainSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        model = Chain
        fields = ('id', 'name', 'messages')

class GameSerializer(serializers.ModelSerializer):
    chains = ChainSerializer(many=True)

    class Meta:
        model = Game
        fields = ('id', 'name', 'chains')
