from django.core.management.base import BaseCommand, CommandError

from grunt.models import Game, Chain, Message
from ratings.forms import NewSurveyForm

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Args for creating the survey
        parser.add_argument('name', help='The name of the survey')
        parser.add_argument('--num-questions-per-player', '-p', type=int, default=10,
                            help='Default is 10 questions')
        parser.add_argument('--determine-correct', '-d', action='store_true', default=False,
                            help='Default is not to determine a correct answer')
        parser.add_argument('--choices', '-c', nargs='+', type=int,
                            required=True, help='Choices (message ids) for this survey')

        # Args for selecting the questions for the survey
        parser.add_argument('--game-id', '-g', type=int, required=True,
                            help='The id of the game to search for messages')
        parser.add_argument('--generations', '-n', nargs='+', type=int, default=-1,
                            help='Defaults to all generations')
        parser.add_argument('--include', '-i', nargs='+', type=int,
                            required=False, help='Branches of messages to include (seed message ids)')
        parser.add_argument('--exclude', '-x', nargs='+', type=int,
                            required=False, help='Branches to messages exclude (seed message ids)')
        parser.add_argument('--extra', '-e', nargs='+', type=int,
                            required=False, help='Additional questions to add to the survey')
        parser.add_argument('--include-rejects', action='store_true', default=False)

    def handle(self, *args, **options):
        """Create a survey via form kwargs passed from the command line."""
        questions = determine_questions(**options)
        keys = ['name', 'num_questions_per_player', 'determine_correct']
        data = {k: options[k] for k in keys}
        data['choices'] = id_str(options['choices'])
        data['questions'] = id_str(determine_questions(**options))
        form = NewSurveyForm(data)
        if not form.is_valid():
            raise CommandError('form not valid:\n\n{}\n\n'.format(form.errors))
        survey = form.save()

def determine_questions(game_id=None, generations=None, include_rejects=False,
                        include=None, exclude=None, extra=None, **options):
    """Select some subset of a game's messages to use in a survey."""
    try:
        game = Game.objects.get(pk=int(game_id))
    except Game.DoesNotExist:
        msg = 'game {} does not exist'
        raise CommandError(msg.format(game_id))

    messages = game.get_messages_by_generation(generations)

    if not include_rejects:
        messages = messages.filter(rejected=False)

    def find_seed(message):
        if message.generation == 0:
            return message.pk
        return find_seed(message.parent)

    seed_map = {}
    for message in messages:
        seed_map[message.pk] = find_seed(message)

    message_ids = [m.pk for m in messages]

    if include:
        message_ids = [m for m in message_ids if seed_map[m] in include]

    if exclude:
        message_ids = [m for m in message_ids if seed_map[m] not in exclude]

    if extra:
        message_ids += extra

    return message_ids

def id_str(message_ids):
    """Format a list of ints into a format that is expected by the form field."""
    return ','.join(map(str, message_ids))
