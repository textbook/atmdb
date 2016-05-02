import asyncio
from http import HTTPStatus

from asynctest import mock
import pytest

from atmdb import TMDbClient

TOKEN = 'some_api_token'


def future_from(result):
    future = asyncio.Future()
    future.set_result(result)
    return future


@pytest.fixture
def client():
    return TMDbClient(api_token=TOKEN)


def test_client_instantiation(client):
    assert client.api_token == TOKEN


def test_client_auth(client):
    expected = 'https://api.themoviedb.org/3/endpoint'
    assert client.url_builder('endpoint') == (expected, dict(api_key=TOKEN))


@pytest.mark.asyncio
async def test_get_movie(client):
    body = '{"original_title":"Test Movie"}'.encode('utf-8')
    target = 'atmdb.client.aiohttp'
    with mock.patch(target) as aiohttp:
        aiohttp.get.return_value = future_from(mock.MagicMock(
            status=HTTPStatus.OK,
            **{'read.return_value': future_from(body)},
        ))

        movie = await client.get_movie(550)

        assert movie.title == 'Test Movie'
        aiohttp.get.assert_called_once_with(
            'https://api.themoviedb.org/3/movie/550',
            params=dict(api_key=TOKEN),
        )
