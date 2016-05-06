"""API client wrapper."""
import asyncio
from collections import OrderedDict
from datetime import datetime, timedelta
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

    def __init__(self, *, api_token, **kwargs):
        super().__init__(api_token=api_token, **kwargs)
        self.config = dict(data=None, last_update=None)

    @property
    def headers(self):
        return dict(Accept='application/json', **super().headers)

    @property
    def config_expired(self):
        """Whether the configuration data has expired."""
        return (self.config['last_update'] + timedelta(days=2)) < datetime.now()

    async def update_config(self):
        """Update configuration data if required.

        Notes:
          Per `the documentation`_, this updates the API configuration
          data *"every few days"*.

        .. _the documentation:
          http://docs.themoviedb.apiary.io/#reference/configuration

        """
        if self.config['data'] is None or self.config_expired:
            data = await self._get_data(self.url_builder('configuration'))
            self.config = dict(data=data, last_update=datetime.now())

    async def _get_data(self, url):
        """Get data from the TMDb API via :py:func:`aiohttp.get`.

        Arguments:
          url (:py:class:`str`): The endpoint URL and params.

        Returns:
          :py:class:`dict`: The parsed JSON result.

        """
        if url != self.url_builder('configuration'):
            await self.update_config()
        logger.debug('making request to %r', url)
        with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                body = json.loads((await response.read()).decode('utf-8'))
                if response.status == HTTPStatus.OK:
                    return body
                elif response.status == HTTPStatus.TOO_MANY_REQUESTS:
                    timeout = self.calculate_timeout(response.headers)
                    logger.info(
                        'Request limit exceeded, waiting %s seconds',
                        timeout,
                    )
                    await asyncio.sleep(timeout)
                    return await self._get_data(url)
                logger.warning(
                    'request failed %s: %r',
                    response.status,
                    body.get('status_message', '<no message>')
                )

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
            return
        return Person.from_json(data)
