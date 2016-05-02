class Movie:
    """Represents movies.

    Arguments:
      title (:py:class:`str`): The title of the movie.

    """

    def __init__(self, title):
        self.title = title

    @classmethod
    def from_json(cls, json):
        """Instantiate class from JSON response data."""
        return cls(json['original_title'])
