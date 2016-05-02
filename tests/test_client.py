from atmdb import TMDbClient


def test_client_instantiation():
    key = 'some_api_key'
    client = TMDbClient(key)
    assert client.api_key == key
