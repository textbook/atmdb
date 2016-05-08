import pytest

from atmdb.models import BaseModel


@pytest.fixture
def base_model(config):
    return BaseModel.from_json(dict(id=1), config['data']['images'])


def test_base_model(base_model):
    assert base_model == BaseModel(id_=1)
    assert repr(base_model) == 'BaseModel(id_=1)'
    assert hash(base_model) == hash(1)


def test_create_image_url(base_model):
    assert base_model._create_image_url(
        '/8uO0gUM8aNqYLs1OsTBQiXu0fEv.jpg',
        'poster',
        500,
    ) == 'https://image.tmdb.org/t/p/w500/8uO0gUM8aNqYLs1OsTBQiXu0fEv.jpg'


def test_create_image_url_no_config(base_model):
    base_model.image_config = None
    assert base_model._create_image_url('foo', 'bar', 123) is None


@pytest.mark.parametrize('type_,target,expected', [
    ('poster', 300, 'w342'),
    ('poster', 500, 'w500'),
    ('profile', 300, 'w185'),
    ('profile', 500, 'h632'),
])
def test_image_size(config, base_model, type_, target, expected):
    assert base_model._image_size(
        config['data']['images'],
        type_,
        target,
    ) == expected
