"""API client wrapper."""
from http import HTTPStatus
import json
import logging

import aiohttp

from .core import UrlParamMixin, Service
from .models import Movie

logger = logging.getLogger(__name__)


class TMDbClient(UrlParamMixin, Service):
    """Simple wrapper for the `TMDb`_ API.

    .. _TMDb: https://www.themoviedb.org/

    """

    AUTH_PARAM = 'api_key'

    ROOT = 'https://api.themoviedb.org/3/'

    async def get_movie(self, movie_id):
        """Retrieve movie data by ID.

        Arguments:
          movie_id (:py:class:`int`): The movie's TMDb ID.

        """
        url = self.url_builder('movie/{movie_id}', dict(movie_id=movie_id))
        logger.debug('making request to %r', url)
        response = await aiohttp.get(url)
        if response.status != HTTPStatus.OK:
            return None
        body = await response.read()
        return Movie.from_json(json.loads(body))
