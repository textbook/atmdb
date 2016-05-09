"""Models representing TMDb resources."""
import logging

logger = logging.getLogger(__name__)


class BaseModel:
    """Base TMDb model functionality.

    Arguments:
      image_config (:py:class:`dict`): The API image configuration.
      id_ (:py:class:`int`): The TMDb ID of the object.

    """

    CONTAINS = None
    """:py:class:`dict`: Rules for what the model contains."""

    IMAGE_TYPE = None
    """:py:class:`str`: The type of image to use."""

    JSON_MAPPING = dict(id_='id')
    """:py:class:`dict`: The mapping between JSON keys and attributes."""

    image_config = None

    def __init__(self, *, id_, image_path=None, **_):
        self.id_ = id_
        self.image_path = image_path

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

    @property
    def image_url(self):
        """The fully-qualified image URL."""
        return self._create_image_url(self.image_path, self.IMAGE_TYPE, 200)

    def _create_image_url(self, file_path, type_, target_size):
        """The the closest available size for specified image type.

        Arguments:
          file_path (:py:class:`str`): The image file path.
          type_ (:py:class:`str`): The type of image to create a URL
            for, (``'poster'`` or ``'profile'``).
          target_size (:py:class:`int`): The size of image to aim for (used
            as either width or height).

        """
        if self.image_config is None:
            logger.warning('no image configuration available')
            return
        return ''.join([
            self.image_config['secure_base_url'],
            self._image_size(self.image_config, type_, target_size),
            file_path,
        ])

    @classmethod
    def from_json(cls, json, image_config=None):
        """Create a model instance

        Arguments:
          json (:py:class:`dict`): The parsed JSON data.
          image_config (:py:class:`dict`): The API image configuration
            data.

        Returns:
          :py:class:`BaseModel`: The model instance.

        """
        cls.image_config = image_config
        return cls(**{
            attr: json.get(key) for attr, key in cls.JSON_MAPPING.items()
        })

    @staticmethod
    def _image_size(image_config, type_, target_size):
        """Find the closest available size for specified image type.

        Arguments:
          image_config (:py:class:`dict`): The image config data.
          type_ (:py:class:`str`): The type of image to create a URL
            for, (``'poster'`` or ``'profile'``).
          target_size (:py:class:`int`): The size of image to aim for (used
            as either width or height).

        """
        return min(
            image_config['{}_sizes'.format(type_)],
            key=lambda size: (abs(target_size - int(size[1:]))
                              if size.startswith('w') or size.startswith('h')
                              else 999),
        )


class Movie(BaseModel):
    """Represents a movie.

    Arguments:
      title (:py:class:`str`): The title of the movie.
      cast (:py:class:`set`, optional): The movie's cast.

    """

    CONTAINS = dict(attr='cast', image_path='poster_path', type='Person')

    IMAGE_TYPE = 'poster'

    JSON_MAPPING = dict(
        cast='cast',
        image_path='{}_path'.format(IMAGE_TYPE),
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
    def from_json(cls, json, image_config=None):
        json['cast'] = {
            Person.from_json(person) for person in
            json.get('credits', {}).get('cast', [])
        } or None
        return super().from_json(json, image_config)


class Person(BaseModel):
    """Represents a person.

    Arguments:
      name (:py:class:`str`): The person's name.
      movie_credits (:py:class:`set`, optional): The person's movie
        credits.

    """

    CONTAINS = dict(attr='movie_credits', type='Movie')

    IMAGE_TYPE = 'profile'

    JSON_MAPPING = dict(
        image_path='{}_path'.format(IMAGE_TYPE),
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
    def from_json(cls, json, image_config=None):
        json['movie_credits'] = {
            Movie.from_json(movie) for movie in
            json.get('movie_credits', {}).get('cast', [])
        } or None
        return super().from_json(json, image_config)
