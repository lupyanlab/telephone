import unittest
from unipath import Path

from django.conf import settings

from grunt import handlers
from grunt.views import VOLUME_CUTOFF_dBFS


class MicCheckTest(unittest.TestCase):
    def test_acceptable_volume(self):
        normal_volume = Path(settings.APP_DIR,
                             'grunt/tests/media/test-audio.wav')
        with open(normal_volume, 'rb') as open_audio:
            mic_checked = handlers.check_volume(open_audio)

        self.assertGreater(mic_checked, VOLUME_CUTOFF_dBFS)

    def test_too_quiet(self):
        quiet_volume = Path(settings.APP_DIR,
                            'grunt/tests/media/test-audio-quiet.wav')
        with open(quiet_volume, 'rb') as open_audio:
            mic_checked = handlers.check_volume(open_audio)

        self.assertLess(mic_checked, VOLUME_CUTOFF_dBFS)
