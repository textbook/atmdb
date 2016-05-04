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
async def test_get_object():
    with mock.patch('atmdb.client.aiohttp') as aiohttp:
        aiohttp.get.return_value = future_from(mock.MagicMock(
            status=HTTPStatus.OK,
            **{'read.return_value': future_from('{}'.encode('utf-8'))}
        ))
        url = 'url'
        params = {'some': 'params'}

        result = await TMDbClient.get_data(url, params)

        aiohttp.get.assert_called_once_with(url, params=params)
        assert result == {}


@pytest.mark.asyncio
async def test_get_no_object():
    with mock.patch('atmdb.client.aiohttp') as aiohttp:
        aiohttp.get.return_value = future_from(mock.MagicMock(
            status=HTTPStatus.NOT_FOUND,
        ))
        result = await TMDbClient.get_data('', {})

        aiohttp.get.assert_called_once_with('', params={})
        assert result is None


@pytest.mark.asyncio
async def test_get_movie(client):
    with mock.patch.object(TMDbClient, 'get_data') as get_data:
        get_data.return_value = future_from(dict(id=1, original_title='Test Movie'))

        movie = await client.get_movie(123)

        assert movie.title == 'Test Movie'
        get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/movie/123',
            dict(api_key=TOKEN, append_to_response='credits'),
        )


@pytest.mark.asyncio
async def test_get_person(client):
    with mock.patch.object(TMDbClient, 'get_data') as get_object:
        get_object.return_value = future_from(dict(id=1, name='Some Name'))

        person = await client.get_person(123)

        assert person.name == 'Some Name'
        get_object.assert_called_once_with(
            'https://api.themoviedb.org/3/person/123',
            dict(api_key=TOKEN, append_to_response='movie_credits'),
        )


@pytest.mark.asyncio
async def test_find_person(client):
    with mock.patch.object(TMDbClient, 'get_data') as get_data:
        get_data.return_value = future_from({
            'results': [{'id': 1, 'name': 'Some Person'}],
        })

        result = await client.find_person('some person')

        assert result[0].name == 'Some Person'
        get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/search/person',
            dict(api_key=TOKEN, include_adult=False, query='some%20person')
        )
