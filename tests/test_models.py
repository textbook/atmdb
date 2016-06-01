from datetime import date
from textwrap import dedent

from atmdb.models import Movie, Person


def test_movie_model():
    title = 'Some Title'
    cast = [{'some': 'actors', 'id': 1}]
    movie = Movie(id_=1, title=title, cast=cast)
    assert movie.title == title
    assert movie.cast == cast


def test_movie_model_from_json():
    title = 'Some Title'
    name = 'Some Person'
    movie = Movie.from_json(dict(
        id=1,
        original_title=title,
        credits=dict(
            cast=[{'name': name, 'id': 1}],
        ),
        release_date='2012-05-08',
    ))
    assert movie.title == title
    assert movie.cast == {Person(id_=1, name=name)}
    assert movie.release_date == date(2012, 5, 8)
    assert movie.release_year == 2012


def test_person_model():
    name = 'Some Person'
    credits_ = [{'some': 'thing', 'id': 1}]
    person = Person(id_=1, name=name, movie_credits=credits_)
    assert person.name == name
    assert person.movie_credits == credits_


def test_person_model_from_json():
    name = 'Some Person'
    title = 'Some Title'
    person = Person.from_json(dict(
        id=1,
        name=name,
        movie_credits=dict(
            cast=[{'original_title': title, 'id': 1}],
        )
    ))
    assert person.name == name
    assert person.movie_credits == {Movie(id_=1, title=title)}


def test_movie_model_contains_person():
    star = Person(id_=2, name='')
    movie = Movie(id_=1, title='', cast=[star])
    assert star in movie


def test_person_model_contains_movie():
    movie = Movie(id_=1, title='')
    star = Person(id_=2, name='', movie_credits=[movie])
    assert movie in star


def test_movie_model_full_str():
    movie = Movie(id_=123, title='Test Movie', synopsis='Just some movie.')
    assert str(movie) == dedent("""
    *Test Movie*

    Just some movie.

    For more information see: https://www.themoviedb.org/movie/123
    """).strip()


def test_person_model_full_str():
    movie = Person(id_=123, name='Some Person', biography='An actor, I guess.')
    assert str(movie) == dedent("""
    *Some Person*

    An actor, I guess.

    For more information see: https://www.themoviedb.org/person/123
    """).strip()


def test_movie_model_short_str():
    movie = Movie(id_=123, title='Test Movie')
    assert str(movie) == dedent("""
    Test Movie [https://www.themoviedb.org/movie/123]
    """).strip()


def test_person_model_short_str():
    movie = Person(id_=123, name='Some Person')
    assert str(movie) == dedent("""
    Some Person [https://www.themoviedb.org/person/123]
    """).strip()
