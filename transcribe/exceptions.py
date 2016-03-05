
class SurveyCompleteException(Exception):
    """This user has completed the required number of questions."""


class NoMoreMessagesException(Exception):
    """There are no more messages that haven't been completed."""
