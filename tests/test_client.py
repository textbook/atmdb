import asyncio
from datetime import datetime, timedelta, timezone

from asynctest import mock
import pytest

from atmdb import TMDbClient

CONFIG = dict(
    data=dict(
        change_keys=[],
        images=dict(
            poster_sizes=['w92', 'w154', 'w185', 'w342', 'w500', 'w780', 'original'],
            profile_sizes=['w45', 'w185', 'h632', 'original'],
            secure_base_url='https://image.tmdb.org/t/p/',
        ),
    ),
    last_update=datetime.now(),
)

TOKEN = 'some_api_token'


def future_from(result):
    future = asyncio.Future()
    future.set_result(result)
    return future


@pytest.fixture
def client():
    instance = TMDbClient(api_token=TOKEN)
    instance.config = CONFIG
    return instance


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


def test_calculate_timeout_delta_seconds():
    assert TMDbClient.calculate_timeout({'Retry-After': '120'}) == 120


def test_calculate_timeout_http_date():
    three_minutes_later = datetime.now(tz=timezone.utc) + timedelta(minutes=3)
    http_date = '%a, %d %b %Y %H:%M:%S %Z'
    headers = {'Retry-After': three_minutes_later.strftime(http_date)}
    assert 179 <= TMDbClient.calculate_timeout(headers) <= 181


@pytest.mark.asyncio
async def test_update_config_missing(client):
    with mock.patch.object(TMDbClient, '_get_data') as _get_data:
        client.config = dict(data=None, last_update=None)
        data = {'some': 'data'}
        _get_data.return_value = future_from(data)

        await client.update_config()

        assert client.config.get('data') == data
        assert isinstance(client.config.get('last_update'), datetime)
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/configuration?api_key={}'.format(TOKEN)
        )


@pytest.mark.asyncio
async def test_update_config_outdated(client):
    with mock.patch.object(TMDbClient, '_get_data') as _get_data:
        data = {'some': 'data'}
        _get_data.return_value = future_from(data)
        last_week = datetime.now() - timedelta(days=7)
        client.config = dict(data={}, last_update=last_week)

        await client.update_config()

        assert client.config.get('data') == data
        assert isinstance(client.config.get('last_update'), datetime)
        assert client.config.get('last_update') != last_week
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/configuration?api_key={}'.format(TOKEN)
        )


@pytest.mark.asyncio
async def test_update_config_up_to_date(client):
    with mock.patch.object(TMDbClient, '_get_data') as _get_data:
        await client.update_config()

        assert client.config == CONFIG
        _get_data.assert_not_called()


def test_create_image_url(client):
    assert client._create_image_url(
        '/8uO0gUM8aNqYLs1OsTBQiXu0fEv.jpg',
        'poster',
        500,
    ) == 'https://image.tmdb.org/t/p/w500/8uO0gUM8aNqYLs1OsTBQiXu0fEv.jpg'


def test_create_image_url_no_config(client):
    client.config = dict(data=None, last_update=None)
    assert client._create_image_url('foo', 'bar', 123) is None


@pytest.mark.parametrize('type_,target,expected', [
    ('poster', 300, 'w342'),
    ('poster', 500, 'w500'),
    ('profile', 300, 'w185'),
    ('profile', 500, 'h632'),
])
def test_image_size(type_, target, expected):
    assert TMDbClient._image_size(
        CONFIG['data']['images'],
        type_,
        target,
    ) == expected
