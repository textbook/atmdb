import pytest
from asynctest import mock

from atmdb.models import Movie, Person
from atmdb.utils import overlapping_actors, overlapping_movies


@pytest.mark.asyncio
async def test_overlapping_movies_no_client():
        person1 = Person(
            id_=1,
            movie_credits={Movie(id_=1, title=''), Movie(id_=2, title='')},
            name='',
        )
        person2 = Person(
            id_=2,
            movie_credits={Movie(id_=2, title=''), Movie(id_=3, title='')},
            name='',
        )
        person3 = Person(
            id_=2,
            movie_credits={Movie(id_=2, title=''), Movie(id_=4, title='')},
            name='',
        )

        movies = await overlapping_movies([person1, person2, person3])

        assert len(movies) == 1
        assert Movie(id_=2, title='') in movies


@pytest.mark.asyncio
async def test_overlapping_movies(client):
    with mock.patch.object(client, 'get_movie') as get_movie:
        person1 = Person(
            id_=1,
            movie_credits={Movie(id_=1, title=''), Movie(id_=2, title='')},
            name='',
        )
        person2 = Person(
            id_=2,
            movie_credits={Movie(id_=2, title=''), Movie(id_=3, title='')},
            name='',
        )
        person3 = Person(
            id_=2,
            movie_credits={Movie(id_=2, title=''), Movie(id_=4, title='')},
            name='',
        )
        get_movie.return_value = Movie(id_=2, title='')

        movies = await overlapping_movies([person1, person2, person3], client)

        assert len(movies) == 1
        assert Movie(id_=2, title='') in movies
        get_movie.assert_called_once_with(id_=2)


@pytest.mark.asyncio
async def test_overlapping_actors_no_client():
        movie1 = Movie(
            id_=1,
            cast={Person(id_=1, name=''), Person(id_=2, name='')},
            title='',
        )
        movie2 = Movie(
            id_=2,
            cast={Person(id_=2, name=''), Person(id_=3, name='')},
            title='',
        )
        movie3 = Movie(
            id_=2,
            cast={Person(id_=2, name=''), Person(id_=4, name='')},
            title='',
        )

        people = await overlapping_actors([movie1, movie2, movie3])

        assert len(people) == 1
        assert Person(id_=2, name='') in people


@pytest.mark.asyncio
async def test_overlapping_actors(client):
    with mock.patch.object(client, 'get_person') as get_person:
        movie1 = Movie(
            id_=1,
            cast={Person(id_=1, name=''), Person(id_=2, name='')},
            title='',
        )
        movie2 = Movie(
            id_=2,
            cast={Person(id_=2, name=''), Person(id_=3, name='')},
            title='',
        )
        movie3 = Movie(
            id_=2,
            cast={Person(id_=2, name=''), Person(id_=4, name='')},
            title='',
        )
        get_person.return_value = Person(id_=2, name='')

        people = await overlapping_actors([movie1, movie2, movie3], client)

        assert len(people) == 1
        assert Person(id_=2, name='') in people
        get_person.assert_called_once_with(id_=2)
