from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from asynctest import mock
import pytest

from atmdb import TMDbClient

from tests.helpers import future_from, SimpleSessionMock


def test_client_instantiation(client, token):
    assert client.api_token == token


@mock.patch('atmdb.core.getenv')
def test_client_from_env(getenv, token):
    getenv.return_value = token

    client = TMDbClient.from_env()

    assert client.api_token == token
    getenv.assert_called_once_with(TMDbClient.TOKEN_ENV_VAR)


def test_client_auth(client, token):
    expected = 'https://api.themoviedb.org/3/endpoint?api_key={}'.format(token)
    assert client.url_builder('endpoint') == expected


def test_calculate_timeout_delta_seconds():
    assert TMDbClient.calculate_timeout('120') == 120


def test_calculate_timeout_http_date():
    three_minutes_later = datetime.now(tz=timezone.utc) + timedelta(minutes=3)
    http_date = '%a, %d %b %Y %H:%M:%S %Z'
    assert 179 <= TMDbClient.calculate_timeout(
        three_minutes_later.strftime(http_date),
    ) <= 181


@pytest.mark.asyncio
async def test_get_data_ok(client):
    with mock.patch('atmdb.client.aiohttp.ClientSession', SimpleSessionMock) as session:
        payload = {'some': 'data'}
        session.configure_mock(side_effect=[
            dict(code=HTTPStatus.OK, body=payload),
        ])

        data = await client.get_data('dummy_url')

        assert data == payload
        assert len(session.call_args_list) == 1
        session.assert_called_with('dummy_url', headers=client.headers)


@pytest.mark.asyncio
async def test_get_data_too_many_requests(client):
    with mock.patch('atmdb.client.aiohttp.ClientSession', SimpleSessionMock) as session:
        payload = {'some': 'data'}
        session.configure_mock(side_effect=[
            dict(code=HTTPStatus.TOO_MANY_REQUESTS, headers={'Retry-After': 1}),
            dict(code=HTTPStatus.OK, body=payload),
        ])

        data = await client.get_data('dummy_url')

        assert data == payload
        assert len(session.call_args_list) == 2
        session.assert_called_with('dummy_url', headers=client.headers)


@pytest.mark.asyncio
async def test_get_data_other_error(client):
    with mock.patch('atmdb.client.aiohttp.ClientSession', SimpleSessionMock) as session:
        session.configure_mock(side_effect=[
            dict(code=HTTPStatus.NOT_FOUND, body=dict(status_message='testing error handling')),
        ])

        data = await client.get_data('dummy_url')

        assert data is None
        assert len(session.call_args_list) == 1
        session.assert_called_with('dummy_url', headers=client.headers)


@pytest.mark.asyncio
async def test_get_movie(client, token):
    with mock.patch.object(TMDbClient, 'get_data') as _get_data:
        _get_data.return_value = future_from(dict(id=1, original_title='Test Movie'))

        movie = await client.get_movie(123)

        assert movie.title == 'Test Movie'
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/movie/123'
            '?append_to_response=credits&api_key={}'.format(token),
        )


@pytest.mark.asyncio
async def test_find_movie(client, token):
    with mock.patch.object(TMDbClient, 'get_data') as _get_data:
        _get_data.return_value = future_from({
            'results': [{'id': 1, 'original_title': 'Test Movie'}],
        })

        result = await client.find_movie('test movie')

        assert result[0].title == 'Test Movie'
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/search/movie'
            '?query=test+movie&include_adult=False&api_key={}'.format(token),
        )


@pytest.mark.asyncio
async def test_get_person(client, token):
    with mock.patch.object(TMDbClient, 'get_data') as _get_data:
        _get_data.return_value = future_from(dict(id=1, name='Some Name'))

        person = await client.get_person(123)

        assert person.name == 'Some Name'
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/person/123'
            '?append_to_response=movie_credits&api_key={}'.format(token),
        )


@pytest.mark.asyncio
async def test_find_person(client, token):
    with mock.patch.object(TMDbClient, 'get_data') as _get_data:
        _get_data.return_value = future_from({
            'results': [{'id': 1, 'name': 'Some Person'}],
        })

        result = await client.find_person('some person')

        assert result[0].name == 'Some Person'
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/search/person'
            '?query=some+person&include_adult=False&api_key={}'.format(token),
        )


@pytest.mark.asyncio
async def test_get_random_actor_simple(client, token):
    with mock.patch.object(TMDbClient, 'get_data') as _get_data:
        _get_data.side_effect = [
            future_from({
                'page': 1,
                'results': [{'id': 1, 'name': 'Some Person'}],
                'total_results': 1,
                'total_pages': 1,
            }),
            future_from({'biography': 'extra stuff'}),
        ]

        result = await client.get_random_popular_person(1)

        assert result.name == 'Some Person'
        assert result.biography == 'extra stuff'
        _get_data.assert_has_calls([
            mock.call('https://api.themoviedb.org/3/person/popular'
                      '?page=1&api_key={}'.format(token)),
            mock.call('https://api.themoviedb.org/3/person/1'
                      '?api_key={}'.format(token)),
        ])


@pytest.mark.asyncio
async def test_get_random_actor_paged(client, token):
    with mock.patch.object(TMDbClient, 'get_data') as _get_data, \
            mock.patch('atmdb.client.random.randrange', return_value=15) as randrange:
        first_page = future_from({
            'page': 1,
            'results': [{}] * 10,
            'total_results': 20,
            'total_pages': 2,
        })
        second_page = future_from({
            'page': 2,
            'results': ([{}] * 4) + [{'id': 1, 'name': 'Some Person'}, {}],
            'total_results': 20,
            'total_pages': 2,
        })
        person = future_from({'biography': 'extra stuff'})
        _get_data.side_effect = [first_page, second_page, person]

        result = await client.get_random_popular_person(1)

        assert result.name == 'Some Person'
        assert result.biography == 'extra stuff'
        _get_data.assert_has_calls([
            mock.call('https://api.themoviedb.org/3/person/popular'
                      '?page=1&api_key={}'.format(token)),
            mock.call('https://api.themoviedb.org/3/person/popular'
                      '?page=2&api_key={}'.format(token)),
            mock.call('https://api.themoviedb.org/3/person/1'
                      '?api_key={}'.format(token)),
        ])
