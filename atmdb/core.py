"""Core API wrapper functionality, adapted from `Flash Services`_.

.. _Flash Services:
    https://pypi.python.org/pypi/flash-services

"""
# pylint: disable=too-few-public-methods
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from datetime import datetime, timezone
from urllib.parse import urlencode

from dateutil.parser import parse


class Service(metaclass=ABCMeta):
    """Abstract base class for API wrapper services."""

    REQUIRED = set()
    """:py:class:`set`: The service's required configuration keys."""

    ROOT = ''
    """:py:class:`str`: The root URL for the API."""

    @abstractmethod
    def __init__(self, *_, **kwargs):
        self.service_name = kwargs.get('name')

    @property
    def headers(self):
        """Get the headers for the service requests.

        Returns:
          :py:class:`dict`: The header mapping.

        """
        return {}

    def url_builder(self, endpoint, *, root=None, params=None, url_params=None):
        """Create a URL for the specified endpoint.

        Arguments:
          endpoint (:py:class:`str`): The API endpoint to access.
          root: (:py:class:`str`, optional): The root URL for the
            service API.
          params: (:py:class:`dict`, optional): The values for format
            into the created URL (defaults to ``None``).
          url_params: (:py:class:`dict`, optional): Parameters to add
            to the end of the URL (defaults to ``None``).

        Returns:
          :py:class:`str`: The resulting URL.

        """
        if root is None:
            root = self.ROOT
        return ''.join([
            root,
            endpoint,
            '?' + urlencode(url_params) if url_params else '',
        ]).format(**params or {})

    @staticmethod
    def calculate_timeout(headers):
        """Extract request timeout from ``Retry-After`` header.

        Notes:
          Per :rfc:`2616#section-14.37`, the ``Retry-After`` header can
          be either an integer number of seconds or an HTTP date. This
          function can handle either.

        Arguments:
          headers (:py:class:`aiohttp.CIMultiDictProxy`): The response
            headers.

        Returns:
          :py:class:`int`: The timeout, in seconds.

        """
        after = headers['Retry-After']
        try:
            return int(after)
        except ValueError:
            date_after = parse(after)
        utc_now = datetime.now(tz=timezone.utc)
        return int((date_after - utc_now).total_seconds())


class TokenAuthMixin:
    """Mix-in class for implementing token authentication.

    Arguments:
      api_token (:py:class:`str`): A valid API token.

    """

    def __init__(self, *, api_token, **kwargs):
        self.api_token = api_token
        super().__init__(**kwargs)


class UrlParamMixin(TokenAuthMixin):
    """Mix-in class for implementing URL parameter authentication.

    Attributes:
      AUTH_PARAM (:py:class:`str`): The name of the URL parameter to
        supply the token as.
    """

    def url_builder(self, endpoint, params=None, url_params=None):
        """Add authentication URL parameter."""
        if url_params is None:
            url_params = OrderedDict()
        url_params[self.AUTH_PARAM] = self.api_token
        return super().url_builder(
            endpoint,
            params=params,
            url_params=url_params,
        )
