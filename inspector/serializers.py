
from rest_framework import serializers

from grunt.models import Chain, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'parent', 'audio', 'generation', 'alive')

class ChainSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        model = Chain
        fields = ('id', 'name', 'messages')
