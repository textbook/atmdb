aTMDb
=====

Asynchronous API wrapper for `The Movie DB`_.

Usage
-----

The core ``TMDbClient`` must be instantiated with a valid API token (see the
`API FAQ`_ for more information)::

    from atmdb import TMDbClient

    client = TMDbClient(api_token='<insert your token here>')

You can then access the API by calling asynchronous helper methods on the
``client`` instance::

    movie = await client.get_movie(550)
    assert movie.title == 'Fight Club'

.. _API FAQ:
    https://www.themoviedb.org/faq/api
.. _The Movie DB:
    https://www.themoviedb.org/
