from unipath import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from grunt.models import Game, Chain, Message

class Command(BaseCommand):
    def handle(self, *args, **options):
        NUM_CHILDREN = 4

        games = [
            ("Fidelity Game 1", ["riri", "frict", "huuh", "splash"]),
            ("Fidelity Game 2", ["ruru", "frip", "heeh", "splish"]),
            ("Fidelity Game 3", ["water-o", "water-p", "water-s", "water-v"]),
            ("Fidelity Game 4", ["frict-p", "frict-r", "frict-s", "frict-w"]),
        ]

        for name, seeds in games:
            game, created = Game.objects.get_or_create(name=name)
            for name in seeds:
                chain = game.chains.create(name=name)
                message = chain.messages.create(audio=self.get_fixture_file(name))
                message.num_children = NUM_CHILDREN
                message.save()

    def get_fixture_file(self, name):
        fixture_file = Path(settings.APP_DIR, 'grunt/fixtures/{}.wav'.format(name))
        if not fixture_file.exists():
            raise CommandError(fixture_file + ' does not exist')
        return File(open(fixture_file, 'rb'))
