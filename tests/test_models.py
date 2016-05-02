from atmdb.models import Movie, Person


def test_movie_model():
    title = 'Some Title'
    cast = [{'some': 'actors'}]
    movie = Movie(title, cast)
    assert movie.title == title
    assert movie.cast == cast


def test_movie_model_from_json():
    title = 'Some Title'
    name = 'Some Person'
    movie = Movie.from_json(dict(
        original_title=title,
        credits=dict(
            cast=[{'name': name}],
        ),
    ))
    assert movie.title == title
    assert movie.cast == [Person(name)]


def test_person_model():
    name = 'Some Person'
    credits_ = [{'some': 'thing'}]
    person = Person(name, credits_)
    assert person.name == name
    assert person.movie_credits == credits_


def test_person_model_from_json():
    name = 'Some Person'
    title = 'Some Title'
    person = Person.from_json(dict(
        name=name,
        movie_credits=dict(
            cast=[{'original_title': title}],
        )
    ))
    assert person.name == name
    assert person.movie_credits == [Movie(title)]
