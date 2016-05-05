import asyncio

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
    expected = 'https://api.themoviedb.org/3/endpoint?api_key={}'.format(TOKEN)
    assert client.url_builder('endpoint') == expected


@pytest.mark.asyncio
async def test_get_movie(client):
    with mock.patch.object(TMDbClient, '_get_data') as _get_data:
        _get_data.return_value = future_from(dict(id=1, original_title='Test Movie'))

        movie = await client.get_movie(123)

        assert movie.title == 'Test Movie'
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/movie/123'
            '?append_to_response=credits&api_key={}'.format(TOKEN),
        )


@pytest.mark.asyncio
async def test_find_movie(client):
    with mock.patch.object(TMDbClient, '_get_data') as _get_data:
        _get_data.return_value = future_from({
            'results': [{'id': 1, 'original_title': 'Test Movie'}],
        })

        result = await client.find_movie('test movie')

        assert result[0].title == 'Test Movie'
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/search/movie'
            '?query=test+movie&include_adult=False&api_key={}'.format(TOKEN),
        )



@pytest.mark.asyncio
async def test_get_person(client):
    with mock.patch.object(TMDbClient, '_get_data') as _get_data:
        _get_data.return_value = future_from(dict(id=1, name='Some Name'))

        person = await client.get_person(123)

        assert person.name == 'Some Name'
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/person/123'
            '?append_to_response=movie_credits&api_key={}'.format(TOKEN),
        )


@pytest.mark.asyncio
async def test_find_person(client):
    with mock.patch.object(TMDbClient, '_get_data') as _get_data:
        _get_data.return_value = future_from({
            'results': [{'id': 1, 'name': 'Some Person'}],
        })

        result = await client.find_person('some person')

        assert result[0].name == 'Some Person'
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/search/person'
            '?query=some+person&include_adult=False&api_key={}'.format(TOKEN),
        )
