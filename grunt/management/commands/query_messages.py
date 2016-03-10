from django.core.management.base import BaseCommand, CommandError

from grunt.models import Game, Chain, Message

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--game', '-g', type=int, required=True)
        parser.add_argument('--generation', '-n', type=int, default=-1)
        parser.add_argument('--include', '-i', nargs='+', type=int, required=False)
        parser.add_argument('--exclude', '-x', nargs='+', type=int, required=False)
        parser.add_argument('--include-rejects', action='store_true', default=False)

    def handle(self, *args, **options):
        try:
            game = Game.objects.get(pk=options['game'])
        except Game.DoesNotExist:
            msg = 'game {} does not exist'
            raise CommandError(msg.format(options['game']))

        messages = game.get_messages_by_generation(options['generation'])

        if not options['include_rejects']:
            messages = messages.filter(rejected=False)

        def find_seed(message):
            if message.generation == 0:
                return message.pk
            else:
                return find_seed(message.parent)

        seed_map = {}
        for message in messages:
            seed_map[message.pk] = find_seed(message)

        message_ids = [m.pk for m in messages]

        if options['include']:
            message_ids = [m for m in message_ids if seed_map[m] in options['include']]

        if options['exclude']:
            message_ids = [m for m in message_ids if seed_map[m] not in options['exclude']]

        self.stdout.write(','.join(map(str, message_ids)))
