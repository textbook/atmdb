"""Models representing TMDb resources."""


class BaseModel:
    """Base TMDb model functionality.

    Arguments:
      id_ (:py:class:`int`): The TMDb ID of the object.

    """

    CONTAINS = None
    """:py:class:`dict`: Rules for what the model contains."""

    JSON_MAPPING = dict(id_='id')
    """:py:class:`dict`: The mapping between JSON keys and attributes."""

    def __init__(self, id_):
        self.id_ = id_

    def __contains__(self, item):
        if self.CONTAINS is None:
            return False
        attr = self.CONTAINS['attr']
        subclasses = {obj.__name__: obj for obj in
                      BaseModel.__subclasses__()}  # pylint: disable=no-member
        cls = subclasses[self.CONTAINS['type']]
        return isinstance(item, cls) and item in getattr(self, attr)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id_ == other.id_

    def __hash__(self):
        return hash(self.id_)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{}={!r}'.format(attr, getattr(self, attr))
                       for attr in self.JSON_MAPPING]),
        )

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


class Movie(BaseModel):
    """Represents a movie.

    Arguments:
      title (:py:class:`str`): The title of the movie.
      cast (:py:class:`list`, optional): The movie's cast.

    """

    CONTAINS = dict(attr='cast', type='Person')

    JSON_MAPPING = dict(
        cast='cast',
        poster='poster',
        title='original_title',
        **BaseModel.JSON_MAPPING,
    )

    def __init__(self, *, title, cast=None, poster=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.cast = cast
        self.poster = poster

    @classmethod
    def from_json(cls, json):
        json['cast'] = {
            Person.from_json(person) for person in
            json.get('credits', {}).get('cast', [])
        } or None
        return super().from_json(json)


class Person(BaseModel):
    """Represents a person.

    Arguments:
      name (:py:class:`str`): The person's name.
      movie_credits (:py:class:`list`, optional): The person's movie
        credits.

    """

    CONTAINS = dict(attr='movie_credits', type='Movie')

    JSON_MAPPING = dict(
        movie_credits='movie_credits',
        name='name',
        profile='profile',
        **BaseModel.JSON_MAPPING,
    )

    def __init__(self, name, movie_credits=None, profile=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.movie_credits = movie_credits
        self.profile = profile

    @classmethod
    def from_json(cls, json):
        json['movie_credits'] = {
            Movie.from_json(movie) for movie in
            json.get('movie_credits', {}).get('cast', [])
        } or None
        return super().from_json(json)
