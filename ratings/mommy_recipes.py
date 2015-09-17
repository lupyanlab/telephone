from unipath import Path

from django.conf import settings
from django.core.files import File

from model_mommy.recipe import Recipe, foreign_key, related

import grunt.models as grunt_models
import ratings.models as ratings_models


django_file_path = Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')
assert django_file_path.exists()
django_file = File(open(django_file_path, 'rb'))

chain = Recipe(grunt_models.Chain,
    name = 'mommy_chain')

seed = Recipe(grunt_models.Message,
    chain = foreign_key(chain),
    audio = django_file)

recording = Recipe(grunt_models.Message,
    chain = foreign_key(chain),
    parent = foreign_key(seed),
    audio = django_file)

question = Recipe(ratings_models.Question,
    # Needs to be a valid recording
    choices = related('seed', 'seed'),
    answer = foreign_key(seed))

response = Recipe(ratings_models.Response,
    question = foreign_key(question),
    selection = foreign_key(seed))
