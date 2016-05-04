from atmdb.models import BaseModel, Movie, Person


def test_base_model():
    model = BaseModel.from_json(dict(id=1))
    assert model == BaseModel(id_=1)
    assert repr(model) == 'BaseModel(id_=1)'
    assert hash(model) == hash(1)


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
    ))
    assert movie.title == title
    assert movie.cast == {Person(id_=1, name=name)}


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
