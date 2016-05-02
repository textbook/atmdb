from atmdb import TMDbClient


def test_client_instantiation():
    token = 'some_api_token'
    client = TMDbClient(api_token=token)
    assert client.api_token == token


def test_client_auth():
    client = TMDbClient(api_token='something')
    expected = 'https://api.themoviedb.org/3/endpoint?api_key=something'
    assert client.url_builder('endpoint') == expected
