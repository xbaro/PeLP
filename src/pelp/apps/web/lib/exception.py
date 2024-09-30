""" Module implementing exceptions """


class PelpException(Exception):
    """ Generic PeLP exception """
    pass


class PelpCodeException(Exception):
    """ Code related exception """
    pass


class PelpConfigException(Exception):
    """ Configuration related exception """
    pass


class PelpSubmissionException(Exception):
    """ Submission related exception """
    pass


class PelpProjectException(Exception):
    """ Project related exception """
    pass


class PelpExecutionException(Exception):
    """ Execution related exception """
    pass


class PelpLMSException(Exception):
    """ Generic PeLP exception """
    pass

class PelpImportException(Exception):
    """ Generic PeLP exception """
    pass
