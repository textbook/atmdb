"""Core API client class."""


class TMDbClient:
    """

    Arguments:
      api_key (:py:class:`str`) A valid TMDb API key.

    """

    def __init__(self, api_key):
        self.api_key = api_key
