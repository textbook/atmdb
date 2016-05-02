import pytest

from atmdb import TMDbClient

TOKEN = 'some_api_token'

@pytest.fixture
def client():
    return TMDbClient(api_token=TOKEN)


def test_client_instantiation(client):
    assert client.api_token == TOKEN


def test_client_auth(client):
    expected = 'https://api.themoviedb.org/3/endpoint?api_key={}'.format(TOKEN)
    assert client.url_builder('endpoint') == expected
