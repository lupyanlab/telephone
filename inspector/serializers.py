import copy

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

    @property
    def tree_data(self):
        data = copy.deepcopy(self.data)
        chains = data.pop('chains')

        for chain in chains:
            messages = chain.pop('messages')

            def find_children(parent):
                children = [child for child in messages
                            if child['parent'] == parent['id']]
                if children:
                    parent['children'] = children
                    for child in children:
                        find_children(child)

            # Find the seed message
            for message in messages:
                if message['generation'] == 0:
                    seed_message = message
                    break

            # Find children recursively, starting with
            # the seed message
            find_children(seed_message)

            chain['children'] = [seed_message,]

        data['children'] = chains
        return data
