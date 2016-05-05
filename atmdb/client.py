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

    @property
    def headers(self):
        return dict(Accept='application/json', **super().headers)

    async def _get_data(self, url):
        """Get data from the TMDb API via :py:func:`aiohttp.get`.

        Arguments:
          url (:py:class:`str`): The endpoint URL and params.

        Returns:
          :py:class:`dict`: The parsed JSON result.

        """
        logger.debug('making request to %r', url)
        with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status != HTTPStatus.OK:
                    return
                body = await response.read()
                return json.loads(body.decode('utf-8'))

    async def find_movie(self, query):
        """Retrieve movie data by search query.

        Arguments:
          query (:py:class:`str`): Query to search for.

        Returns:
          :py:class:`list`: Possible matches.

        """
        params = OrderedDict([
            ('query', query), ('include_adult', False),
        ])
        url = self.url_builder('search/movie', {}, params)
        data = await self._get_data(url)
        if data is None:
            logger.warning('find_movie failed')
            return
        return [Movie.from_json(item) for item in data.get('results', [])]

    async def find_person(self, query):
        """Retrieve person data by search query.

        Arguments:
          query (:py:class:`str`): Query to search for.

        Returns:
          :py:class:`list`: Possible matches.

        """
        url = self.url_builder(
            'search/person',
            dict(),
            url_params=OrderedDict([
                ('query', query), ('include_adult', False)
            ]),
        )
        data = await self._get_data(url)
        if data is None:
            logger.warning('find_person failed')
            return
        return [Person.from_json(item) for item in data.get('results', [])]

    async def get_movie(self, movie_id):
        """Retrieve movie data by ID.

        Arguments:
          movie_id (:py:class:`int`): The movie's TMDb ID.

        Returns:
          :py:class:`~.Movie`: The requested movie.

        """
        url = self.url_builder(
            'movie/{movie_id}',
            dict(movie_id=movie_id),
            url_params=OrderedDict(append_to_response='credits'),
        )
        data = await self._get_data(url)
        if data is None:
            logger.warning('get_movie failed')
            return
        return Movie.from_json(data)

    async def get_person(self, person_id):
        """Retrieve person data by ID.

        Arguments:
          person_id (:py:class:`int`): The person's TMDb ID.

        Returns:
          :py:class:`~.Person`: The requested person.

        """
        url = self.url_builder(
            'person/{person_id}',
            dict(person_id=person_id),
            url_params=OrderedDict(append_to_response='movie_credits'),
        )
        data = await self._get_data(url)
        if data is None:
            logger.warning('get_person failed')
            return
        return Person.from_json(data)
