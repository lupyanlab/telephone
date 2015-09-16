from unipath import Path
import pydub

def message_file_name(instance, filename):
    """ Message instance must have a chain or a parent to be saved.

    Non-unique file names will not be overwritten.
    """
    chain = instance.chain or instance.parent.chain
    generation = instance.generation or instance.parent.generation + 1
    args = (chain.game.pk, chain.pk, generation)
    return 'game-{}/chain-{}/gen-{}.wav'.format(*args)

def check_volume(recording):
    return pydub.AudioSegment(recording).dBFS
