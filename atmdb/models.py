"""Models representing TMDb resources."""


class BaseModel:
    """Base TMDb model functionality."""

    JSON_MAPPING = {}
    """:py:class:`dict`: The mapping between JSON keys and attributes."""

    @classmethod
    def from_json(cls, json):
        """Create a model instance

        Arguments:
          json (:py:class:`dict`): The parsed JSON data.

        Returns:
          :py:class:`BaseModel`: The model instance.

        """
        return cls(**{
            attr: json.get(key) for attr, key in cls.JSON_MAPPING.items()
        })

    def __eq__(self, other):
        return all(getattr(other, name, None) == getattr(self, name)
                   for name in self.JSON_MAPPING)


class Movie(BaseModel):
    """Represents a movie.

    Arguments:
      title (:py:class:`str`): The title of the movie.
      cast (:py:class:`list`, optional): The movie's cast.

    """

    JSON_MAPPING = dict(cast='cast', title='original_title')

    def __init__(self, title, cast=None):
        self.title = title
        self.cast = cast

    @classmethod
    def from_json(cls, json):
        json['cast'] = [
            Person.from_json(person) for person in
            json.get('credits', {}).get('cast', [])
        ] or None
        return super().from_json(json)


class Person(BaseModel):
    """Represents a person.

    Arguments:
      name (:py:class:`str`): The person's name.
      movie_credits (:py:class:`list`, optional): The person's movie
        credits.

    """

    JSON_MAPPING = dict(movie_credits='movie_credits', name='name')

    def __init__(self, name, movie_credits=None):
        self.name = name
        self.movie_credits = movie_credits

    @classmethod
    def from_json(cls, json):
        json['movie_credits'] = [
            Movie.from_json(movie) for movie in
            json.get('movie_credits', {}).get('cast', [])
        ] or None
        return super().from_json(json)
