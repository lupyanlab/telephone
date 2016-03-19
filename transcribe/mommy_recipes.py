from unipath import Path

from django.conf import settings
from django.core.files import File

from model_mommy.recipe import Recipe, foreign_key, related

import grunt.models as grunt_models
import ratings.models as ratings_models
import transcribe.models as transcribe_models


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

transcription_survey = Recipe(transcribe_models.TranscriptionSurvey)
message_to_transcribe = Recipe(transcribe_models.MessageToTranscribe,
    survey = foreign_key(transcription_survey),
    given = foreign_key(recording),
)
transcription = Recipe(transcribe_models.Transcription,
    message = foreign_key(message_to_transcribe))
