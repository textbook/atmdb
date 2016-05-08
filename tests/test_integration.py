from os import getenv

import pytest

from atmdb import TMDbClient

token = getenv('TMDB_API_TOKEN', None)

if token is not None and pytest.config.getoption('--runslow'):

    @pytest.fixture
    def client():
        return TMDbClient(api_token=token)


    @pytest.mark.asyncio
    async def test_client_additional_endpoints(client):
        url = client.url_builder('company/{company_id}', dict(company_id=508))
        company = await client.get_data(url)
        assert company.get('name') == 'Regency Enterprises'


    @pytest.mark.asyncio
    async def test_missing_data_integration():
        broken_client = TMDbClient(api_token='badtoken')
        result = await broken_client.get_movie(1)
        assert result is None

    @pytest.mark.asyncio
    async def test_movie_integration(client):
        movie = await client.get_movie(550)
        assert movie.title == 'Fight Club'
        assert movie.image_url == 'https://image.tmdb.org/t/p/w185/811DjJTon9gD6hZ8nCjSitaIXFQ.jpg'

    @pytest.mark.asyncio
    async def test_movie_search_integration(client):
        movies = await client.find_movie('fight club')
        assert any(movie.title == 'Fight Club' for movie in movies)

    @pytest.mark.asyncio
    async def test_person_integration(client):
        person = await client.get_person(287)
        assert person.name == 'Brad Pitt'
        assert person.image_url == 'https://image.tmdb.org/t/p/w185/kc3M04QQAuZ9woUvH3Ju5T7ZqG5.jpg'

    @pytest.mark.asyncio
    async def test_person_search_integration(client):
        people = await client.find_person('brad')
        assert any(person.name == 'Brad Pitt' for person in people)
