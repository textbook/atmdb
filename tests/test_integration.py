from os import getenv

import pytest

from atmdb import TMDbClient

token = getenv('TMDB_API_TOKEN', None)

if token is not None:

    slow = pytest.mark.skipif(
        not pytest.config.getoption("--runslow"),
        reason="need --runslow option to run"
    )

    @pytest.fixture
    def client():
        return TMDbClient(api_token=token)

    @slow
    @pytest.mark.asyncio
    async def test_missing_data_integration():
        broken_client = TMDbClient(api_token='badtoken')
        result = await broken_client.get_movie(1)
        assert result is None

    @slow
    @pytest.mark.asyncio
    async def test_movie_integration(client):
        movie = await client.get_movie(550)
        assert movie.title == 'Fight Club'
        assert movie.poster == 'https://image.tmdb.org/t/p/w185/811DjJTon9gD6hZ8nCjSitaIXFQ.jpg'

    @slow
    @pytest.mark.asyncio
    async def test_movie_search_integration(client):
        movies = await client.find_movie('fight club')
        assert any(movie.title == 'Fight Club' for movie in movies)

    @slow
    @pytest.mark.asyncio
    async def test_person_integration(client):
        person = await client.get_person(287)
        assert person.name == 'Brad Pitt'
        assert person.profile == 'https://image.tmdb.org/t/p/w185/kc3M04QQAuZ9woUvH3Ju5T7ZqG5.jpg'

    @slow
    @pytest.mark.asyncio
    async def test_person_search_integration(client):
        people = await client.find_person('brad')
        assert any(person.name == 'Brad Pitt' for person in people)
