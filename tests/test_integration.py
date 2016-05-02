from os import getenv

import pytest

from atmdb import TMDbClient

token = getenv('TMDB_API_TOKEN', None)

if token is not None:

    @pytest.mark.asyncio
    async def test_tmdb_integration():
        client = TMDbClient(api_token=token)
        movie = await client.get_movie(550)
        assert movie.title == 'Fight Club'
