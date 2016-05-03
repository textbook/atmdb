import asyncio
from http import HTTPStatus

from asynctest import mock
import pytest

from atmdb import TMDbClient
from atmdb.models import BaseModel, Movie, Person

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
        response = {'some': 'output'}
        cls = mock.Mock(**{'from_json.return_value': response})

        result = await TMDbClient.get_object(url, params, cls)

        cls.from_json.assert_called_once_with({})
        aiohttp.get.assert_called_once_with(url, params=params)
        assert result == response


@pytest.mark.asyncio
async def test_get_no_object():
    with mock.patch('atmdb.client.aiohttp') as aiohttp:
        aiohttp.get.return_value = future_from(mock.MagicMock(
            status=HTTPStatus.NOT_FOUND,
        ))
        result = await TMDbClient.get_object('', {}, BaseModel)

        aiohttp.get.assert_called_once_with('', params={})
        assert result is None


@pytest.mark.asyncio
async def test_get_movie(client):
    with mock.patch.object(TMDbClient, 'get_object') as get_object:
        get_object.return_value = future_from(Movie(id_=1, title='Test Movie'))

        movie = await client.get_movie(123)

        assert movie.title == 'Test Movie'
        get_object.assert_called_once_with(
            'https://api.themoviedb.org/3/movie/123',
            dict(api_key=TOKEN, append_to_response='credits'),
            Movie,
        )


@pytest.mark.asyncio
async def test_get_person(client):
    with mock.patch.object(TMDbClient, 'get_object') as get_object:
        get_object.return_value = future_from(Person(id_=1, name='Some Name'))

        person = await client.get_person(123)

        assert person.name == 'Some Name'
        get_object.assert_called_once_with(
            'https://api.themoviedb.org/3/person/123',
            dict(api_key=TOKEN, append_to_response='movie_credits'),
            Person,
        )
