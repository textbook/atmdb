aTMDb
=====

.. image:: https://img.shields.io/pypi/v/atmdb.svg
    :target: https://pypi.python.org/pypi/atmdb
    :alt: PyPI Version

.. image:: https://travis-ci.org/textbook/atmdb.svg?branch=master
    :target: https://travis-ci.org/textbook/atmdb
    :alt: Travis Build Status

.. image:: https://coveralls.io/repos/github/textbook/atmdb/badge.svg?branch=master
    :target: https://coveralls.io/github/textbook/atmdb?branch=master
    :alt: Code Coverage

.. image:: https://www.quantifiedcode.com/api/v1/project/370d26a2062c4b148534b576ea0fc11b/badge.svg
    :target: https://www.quantifiedcode.com/app/project/370d26a2062c4b148534b576ea0fc11b
    :alt: Code Issues

.. image:: https://img.shields.io/badge/license-ISC-blue.svg
    :target: https://github.com/textbook/atmdb/blob/master/LICENSE
    :alt: ISC License

Asynchronous API wrapper for `TMDb`_.

Compatibility
-------------

aTMDb uses asyncio_ with the ``async`` and ``await`` syntax, so is only
compatible with Python versions 3.5 and above.

Installation
------------

``atmdb`` can be installed from `PyPI`_ using ``pip``::

    pip install atmdb

Testing
-------

You can run the tests with ``python setup.py test``. To include the integration
suite, ensure that the environment variable ``TMDB_API_TOKEN`` is set to a valid
API token, and use ``--runslow`` if running ``py.test`` directly.

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

Documentation
-------------

Additional documentation is available on `PythonHosted`_.

.. _API FAQ:
    https://www.themoviedb.org/faq/api
.. _PyPI:
    https://pypi.python.org/pypi/atmdb
.. _PythonHosted:
    https://pythonhosted.org/atmdb/
.. _TMDb:
    https://www.themoviedb.org/
