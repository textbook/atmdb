from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from asynctest import mock
import pytest

from atmdb import TMDbClient

from tests.helpers import future_from, SimpleSessionMock


def test_client_instantiation(client, token):
    assert client.api_token == token


def test_client_auth(client, token):
    expected = 'https://api.themoviedb.org/3/endpoint?api_key={}'.format(token)
    assert client.url_builder('endpoint') == expected


def test_calculate_timeout_delta_seconds():
    assert TMDbClient.calculate_timeout({'Retry-After': '120'}) == 120


def test_calculate_timeout_http_date():
    three_minutes_later = datetime.now(tz=timezone.utc) + timedelta(minutes=3)
    http_date = '%a, %d %b %Y %H:%M:%S %Z'
    headers = {'Retry-After': three_minutes_later.strftime(http_date)}
    assert 179 <= TMDbClient.calculate_timeout(headers) <= 181


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
