from unipath import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from grunt.models import Game, Chain, Message

class Command(BaseCommand):
    def handle(self, *args, **options):
        NUM_CHILDREN = 4

        games = {
            "Fidelity Game 1": ["beep", "frick", "huuh", "riri"],
            "Fidelity Game 2": ["boop", "frip", "heeh", "ruru"],
            "Fidelity Game 3": ["beep-d", "beep-e", "beep-o", "beep-z"],
            "Fidelity Game 4": ["frict-g", "frict-j", "frict-l", "frict-w"],
        }

        for name, seeds in games.items():
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
