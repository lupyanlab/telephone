from unipath import Path
import pydub

VOLUME_CUTOFF_dBFS = -20.0

def check_volume(recording):
    audio_segment = pydub.AudioSegment(recording)
    return audio_segment.dBFS > VOLUME_CUTOFF_dBFS


def message_path(instance, filename):
    """ Determine the filename and path for a new audio message """
    message_dir = instance.chain.dirpath()
    stem_kwargs = {'generation': instance.generation}
    message_stem = '{generation}.wav'.format(**stem_kwargs)
    return Path(message_dir, message_stem)
