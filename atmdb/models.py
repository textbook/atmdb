"""Models representing TMDb resources."""
from datetime import date, datetime
import logging
from textwrap import dedent

from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class BaseModel:
    """Base TMDb model functionality.

    Arguments:
      id_ (:py:class:`int`): The TMDb ID of the object.
      image_config (:py:class:`dict`): The API image configuration.
      image_path (:py:class:`str`): The short path to the image.

    Attributes:
      image_url (:py:class:`str`): The fully-qualified image URL.

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
            attr: json.get(attr if key is None else key)
            for attr, key in cls.JSON_MAPPING.items()
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
      synopsis (:py:class:`str`, optional): A synopsis of the movie.
      release_date (:py:class:`datetime.date`): The date of release.

    Attributes:
      release_year (:py:class:`int`) The year of release.
      url (:py:class:`str`): The URL to the movies's TMDb page.

    """

    CONTAINS = dict(attr='cast', image_path='poster_path', type='Person')

    IMAGE_TYPE = 'poster'

    JSON_MAPPING = dict(
        cast=None,
        image_path='{}_path'.format(IMAGE_TYPE),
        release_date=None,
        synopsis='overview',
        title='original_title',
        **BaseModel.JSON_MAPPING,
    )

    def __init__(self, *, title, cast=None, synopsis=None, release_date=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.cast = cast
        self.synopsis = synopsis
        self.title = title
        self.release_date = release_date

    def __str__(self):
        if self.synopsis is None:
            return "{0.title} [{0.url}]".format(self)
        return dedent("""
        *{0.title}*

        {0.synopsis}

        For more information see: {0.url}
        """).strip().format(self)

    @property
    def url(self):
        return 'https://www.themoviedb.org/movie/{}'.format(self.id_)

    @property
    def release_year(self):
        return None if self.release_date is None else self.release_date.year

    @classmethod
    def from_json(cls, json, image_config=None):
        json['cast'] = {
            Person.from_json(person, image_config) for person in
            json.get('credits', {}).get('cast', [])
        } or None
        release = json.get('release_date')
        json['release_date'] = (None if not release else
                                datetime.strptime(release, '%Y-%m-%d').date())
        return super().from_json(json, image_config)


class Person(BaseModel):
    """Represents a person.

    Arguments:
      name (:py:class:`str`): The person's name.
      movie_credits (:py:class:`set`, optional): The person's movie
        credits.
      biography (:py:class:`str`, optional): A synopsis of the movie.
      known_for (:py:class:`list`, optional): A list of the three
        movies the person is best known for.
      birthday (:py:class:`datetime.date`, optional): The person's date
        of birth.

    Attributes:
      age (:py:class:`int`): The person's age, in years.
      url (:py:class:`str`): The URL to the person's TMDb profile.

    """

    CONTAINS = dict(attr='movie_credits', type='Movie')

    IMAGE_TYPE = 'profile'

    JSON_MAPPING = dict(
        biography=None,
        birthday=None,
        image_path='{}_path'.format(IMAGE_TYPE),
        movie_credits=None,
        known_for=None,
        name=None,
        **BaseModel.JSON_MAPPING,
    )

    def __init__(self, name, biography=None, movie_credits=None, known_for=None,
                 birthday=None, **kwargs):
        super().__init__(**kwargs)
        self.biography = biography
        self.movie_credits = movie_credits
        self.name = name
        self.known_for = known_for
        self.birthday = birthday

    def __str__(self):
        if self.biography is None:
            return "{0.name} [{0.url}]".format(self)
        return dedent("""
        *{0.name}*

        {0.biography}

        For more information see: {0.url}
        """).strip().format(self)

    @property
    def age(self):
        if self.birthday is None:
            return
        return relativedelta(date.today(), self.birthday).years

    @property
    def url(self):
        return 'https://www.themoviedb.org/person/{}'.format(self.id_)

    @classmethod
    def from_json(cls, json, image_config=None):
        json['movie_credits'] = {
            Movie.from_json(movie, image_config) for movie in
            json.get('movie_credits', {}).get('cast', [])
        } or None
        json['known_for'] = {
            Movie.from_json(movie, image_config)
            for movie in json.get('known_for', [])
            if movie.get('media_type') == 'movie'
        } or None
        birthday = json.get('birthday')
        json['birthday'] = (None if not birthday else
                            datetime.strptime(birthday, '%Y-%m-%d').date())
        return super().from_json(json, image_config)
