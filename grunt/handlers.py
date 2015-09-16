from unipath import Path
import pydub

from django.utils.text import slugify

def message_file_name(instance, filename):
    """ Message instance must have a chain or a parent to be saved.

    Non-unique file names will not be overwritten.
    """
    chain = instance.chain or instance.parent.chain
    game_dir = slugify(chain.game.name)
    chain_dir = slugify(chain.name)
    if instance.parent:
        gen = instance.parent.generation + 1
        message_name = 'gen-'+str(gen)
    else:
        message_name = 'seed'
    return '{}/{}/{}.wav'.format(game_dir, chain_dir, message_name)

def check_volume(recording):
    return pydub.AudioSegment(recording).dBFS
