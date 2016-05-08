from datetime import datetime, timedelta

from asynctest import mock
import pytest

from atmdb import TMDbClient

from tests.helpers import future_from


@pytest.mark.asyncio
async def test_update_config_missing(client, token):
    with mock.patch.object(TMDbClient, 'get_data') as _get_data:
        client.config = dict(data=None, last_update=None)
        data = {'some': 'data'}
        _get_data.return_value = future_from(data)

        await client._update_config()

        assert client.config.get('data') == data
        assert isinstance(client.config.get('last_update'), datetime)
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/configuration?api_key={}'.format(token)
        )


@pytest.mark.asyncio
async def test_update_config_outdated(client, token):
    with mock.patch.object(TMDbClient, 'get_data') as _get_data:
        data = {'some': 'data'}
        _get_data.return_value = future_from(data)
        last_week = datetime.now() - timedelta(days=7)
        client.config = dict(data={}, last_update=last_week)

        await client._update_config()

        assert client.config.get('data') == data
        assert isinstance(client.config.get('last_update'), datetime)
        assert client.config.get('last_update') != last_week
        _get_data.assert_called_once_with(
            'https://api.themoviedb.org/3/configuration?api_key={}'.format(token)
        )


@pytest.mark.asyncio
async def test_update_config_up_to_date(client, config):
    with mock.patch.object(TMDbClient, 'get_data') as _get_data:
        await client._update_config()

        assert client.config == config
        _get_data.assert_not_called()
