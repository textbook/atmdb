from datetime import datetime

import pytest

from atmdb import TMDbClient


def pytest_addoption(parser):
    parser.addoption(
        "--runslow",
        action="store_true",
        help="run slow tests"
    )


@pytest.fixture
def config():
    return dict(
        data=dict(
            change_keys=[],
            images=dict(
                poster_sizes=['w92', 'w154', 'w185', 'w342', 'w500', 'w780', 'original'],
                profile_sizes=['w45', 'w185', 'h632', 'original'],
                secure_base_url='https://image.tmdb.org/t/p/',
            ),
        ),
        last_update=datetime.now(),
    )


@pytest.fixture
def token():
    return 'some_api_token'


@pytest.fixture
def client(config, token):
    instance = TMDbClient(api_token=token)
    instance.config = config
    return instance
