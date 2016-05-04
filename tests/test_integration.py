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
    async def test_movie_integration(client):
        movie = await client.get_movie(550)
        assert movie.title == 'Fight Club'


    @slow
    @pytest.mark.asyncio
    async def test_person_integration(client):
        person = await client.get_person(287)
        assert person.name == 'Brad Pitt'
