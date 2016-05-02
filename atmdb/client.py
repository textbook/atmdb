"""API client wrapper."""
from .core import UrlParamMixin, Service


class TMDbClient(UrlParamMixin, Service):
    """Simple wrapper for the `TMDb`_ API.

    .. _TMDb: https://www.themoviedb.org/

    """

    AUTH_PARAM = 'api_key'

    ROOT = 'https://api.themoviedb.org/3/'
