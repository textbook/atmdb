"""API client wrapper."""
from collections import OrderedDict
from http import HTTPStatus
import json
import logging

import aiohttp

from .core import UrlParamMixin, Service
from .models import Movie, Person

logger = logging.getLogger(__name__)


class TMDbClient(UrlParamMixin, Service):
    """Simple wrapper for the `TMDb`_ API.

    .. _TMDb: https://www.themoviedb.org/

    """

    AUTH_PARAM = 'api_key'

    ROOT = 'https://api.themoviedb.org/3/'

    @staticmethod
    async def get_object(url, params, cls):
        """Get an object from the TMDb API via :py:func:`aiohttp.get`.

        Arguments:
          url (:py:class:`str`): The endpoint URL.
          params (:py:class:`dict`): URL parameter mapping.
          cls (:py:class:`type`): The type of object to return.

        Returns:
          :py:class:`~.BaseModel`: An instance of the required ``cls``.

        """
        logger.debug('making request to %r', url)
        response = await aiohttp.get(url, params=params)
        if response.status != HTTPStatus.OK:
            return None
        body = await response.read()
        return cls.from_json(json.loads(body.decode('utf-8')))

    async def get_movie(self, movie_id):
        """Retrieve movie data by ID.

        Arguments:
          movie_id (:py:class:`int`): The movie's TMDb ID.

        Returns:
          :py:class:`~.Movie`: The requested movie.

        """
        url, params = self.url_builder(
            'movie/{movie_id}',
            dict(movie_id=movie_id),
            url_params=OrderedDict(append_to_response='credits'),
        )
        return await self.get_object(url, params, Movie)

    async def get_person(self, person_id):
        """Retrieve person data by ID.

        Arguments:
          person_id (:py:class:`int`): The person's TMDb ID.

        Returns:
          :py:class:`~.Person`: The requested person.

        """
        url, params = self.url_builder(
            'person/{person_id}',
            dict(person_id=person_id),
            url_params=OrderedDict(append_to_response='movie_credits'),
        )
        return await self.get_object(url, params, Person)
