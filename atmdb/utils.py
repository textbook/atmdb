"""Utilities for working with TMDb models."""


async def overlapping_movies(people, client=None):
    """Find movies that the same people have been in.

    Arguments:
      people (:py:class:`collections.abc.Sequence`): The
        :py:class:`~.Person` objects to find overlapping movies for.
      client (:py:class:`~.TMDbClient`, optional): The TMDb client
        to extract additional information about the overlap.

    Returns:
      :py:class:`list`: The relevant :py:class:`~.Movie` objects.

    """
    return await _overlap(people, 'movie_credits', client, 'get_movie')


async def overlapping_actors(movies, client=None):
    """Find actors that appear in the same movies.

    Arguments:
      movies (:py:class:`collections.abc.Sequence`): The
        :py:class:`~.Movie` objects to find overlapping actors for.
      client (:py:class:`~.TMDbClient`, optional): The TMDb client
        to extract additional information about the overlap.

    Returns:
      :py:class:`list`: The relevant :py:class:`~.Person` objects.

    """
    return await _overlap(movies, 'cast', client, 'get_person')

async def find_overlapping_movies(names, client):
    """Find movies that the same people have been in.

    Warning:
      This function requires two API calls per name submitted, plus
      one API call per overlapping movie in the result; it is therefore
      relatively slow.

    Arguments:
      names (:py:class:`collections.abc.Sequence`): The names of the
        people to find overlapping movies for.
      client (:py:class:`~.TMDbClient`): The TMDb client.

    Returns:
      :py:class:`list`: The relevant :py:class:`~.Movie` objects.

    """
    return await _find_overlap(names, client, 'find_person', 'get_person',
                               overlapping_movies)


async def find_overlapping_actors(titles, client):
    """Find actors that have been in the same movies.

    Warning:
      This function requires two API calls per title submitted, plus
      one API call per overlapping person in the result; it is therefore
      relatively slow.

    Arguments:
      titles (:py:class:`collections.abc.Sequence`): The titles of the
        movies to find overlapping actors for.
      client (:py:class:`~.TMDbClient`): The TMDb client.

    Returns:
      :py:class:`list`: The relevant :py:class:`~.Person` objects.

    """
    return await _find_overlap(titles, client, 'find_movie', 'get_movie',
                               overlapping_actors)


async def _overlap(items, overlap_attr, client=None, get_method=None):
    """Generic overlap implementation.

    Arguments:
      item (:py:class:`collections.abc.Sequence`): The objects to
        find overlaps for.
      overlap_attr (:py:class:`str`): The attribute of the items to use
        as input for the overlap.
      client (:py:class:`~.TMDbClient`, optional): The TMDb client
        to extract additional information about the overlap.
      get_method (:py:class:`str`, optional): The method of the
        client to use for extracting additional information.

    Returns:
      :py:class:`list`: The relevant result objects.

    """
    overlap = set.intersection(*(getattr(item, overlap_attr) for item in items))
    if client is None or get_method is None:
        return overlap
    results = []
    for item in overlap:
        result = await getattr(client, get_method)(id_=item.id_)
        results.append(result)
    return results


async def _find_overlap(queries, client, find_method, get_method,
                        overlap_function):
    """Generic find and overlap implementation.

    Arguments
      names (:py:class:`collections.abc.Sequence`): The queries of the
        people to find overlaps for.
      client (:py:class:`~.TMDbClient`): The TMDb client.
      find_method (:py:class:`str`): The name of the client method to
        use for finding candidates.
      get_method (:py:class:`str`): The name of the client method to
        use for getting detailed information on a candidate.
      overlap_function (:py:class:`collections.abc.Callable`): The
        function to call for the resulting overlap.

    """
    results = []
    for query in queries:
        candidates = await getattr(client, find_method)(query)
        if not candidates:
            raise ValueError('no result found for {!r}'.format(query))
        result = await getattr(client, get_method)(id_=candidates[0].id_)
        results.append(result)
    return await overlap_function(results, client)
