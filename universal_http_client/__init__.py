# -*- coding: utf-8 -*-
"""Flexible and extensible Python HTTP library wrapper.

While this entry point to the library exposes all classes and functions for
convenience, those items themselves are actually implemented and documented in
child modules.

"""

import os

from validator_collection import validators, checkers

# Get the version number from the _version.py file
version_dict = {}
with open(os.path.join(os.path.dirname(__file__), '__version__.py')) as version_file:
    exec(version_file.read(), version_dict)                                     # pylint: disable=W0122

__version__ = version_dict.get('__version__')

from universal_http_client.HTTPClient import HTTPClient
from universal_http_client.HTTPResponse import HTTPResponse


def get_http_client(client_name, is_third_party = False):
    """Import the :class:`HTTPClient <universal_http_client.HTTPClient.HTTPClient>`
    identified by ``client_name``.

    :param client_name: The name of the
      :class:`HTTPClient <universal_http_client.HTTPClient.HTTPClient>` to return.
    :type client_name: :class:`str <python:str>`

    :param is_third_party: If ``True``, will attempt to import the full path
      indicated by ``client_name``. If ``False``, will expect to find
      ``client_name`` as a module within ``universal_http_client.ext``. Defaults
      to ``False``.
    :type is_third_party: :class:`bool <python:bool>`

    .. note::

      If ``is_third_party`` is ``False``, then ``client_name`` is expected to
      be a valid Python module found in ``universal_http_client.ext``.

    .. warning::

      This function assumes that the extension convention described in the
      :doc:`Contributor Guide <contributing>` is adhered to. This means that
      it expects that the
      :class:`HTTPClient <universal_http_client.HTTPClient.HTTPClient>` class is
      found in a Python module whose name matches the class name.

    :returns: The :class:`HTTPClient <universal_http_client.HTTPClient.HTTPClient>`
      whose name matches ``client_name`` or :obj:`None <python:None>` if it does
      not exist.
    :rtype: :class:`HTTPClient <universal_http_client.HTTPClient.HTTPClient>` /
      :obj:`None <python:None>`

    """
    full_client_name = validators.string(client_name, allow_empty = False)
    package_name = 'universal_http_client.ext'
    if not is_third_party:
        full_client_name = package_name + '.' + full_client_name
    else:
        client_name = client_name.split('.')[-1:]

    try:
        _temp = __import__(full_client_name,
                           globals = globals(),
                           locals = locals(),
                           fromlist = [client_name],
                           level = 0)
    except ImportError:
        return None

    client = getattr(_temp, client_name, None)

    return client

def default_http_client(priority_list = 'RequestsClient|GAEUrlFetchClient|PycurlClient|Urllib3Client|UrlfetchClient|UrllibClient',
                        **kwargs):
    """Retrieve the first available
    :class:`HTTPClient <universal_http_client.HTTPClient.HTTPClient>` listed in
    ``priority_list``.

    :param priority_list: A pipe-delimited list of
      :class:`HTTPClients <universal_http_client.HTTPClient.HTTPClient>` that
      the library will attempt to load in the order listed. As soon as a client
      loads successfully, it will be returned.

      .. tip::

        Regardless of the contents of ``priority_list``, if no client can be
        loaded successfully this function will always return an HTTP client for the
        Python standard library.

      The default priority list is:

        * :doc:`requests <requests:index>`
        * `Google App Engine UrlFetch <https://cloud.google.com/appengine/docs/standard/python/refdocs/google.appengine.api.urlfetch>`_
        * :doc:`pycurl <pycurl:index>`
        * :doc:`urllib3 <urllib3:index>`
        * :doc:`urlfetch <urlfetch:index>`
        * Standard Library: doc:`urllib <python:urllib>` or `urllib2 <python27:urllib2>`

      .. note::

        If you wish to include third-party :class:`HTTPClient <universal_http_client.HTTPClient.HTTPClient>`
        implementations in your priority list, you can do so by specifying the
        full import path (including a ``.`` in their name) to their corresponding
        Python module.

    :type priority_list: :class:`str <python:str>`

    :param kwargs: Additional keyword arguments that are passed to the
      :class:`HTTPClients <universal_http_client.HTTPClient.HTTPClient>` instance.

    :returns: An instance of the first available
      :class:`HTTPClients <universal_http_client.HTTPClient.HTTPClient>` in
      ``priority_list``.
    :rtype: :class:`HTTPClient <universal_http_client.HTTPClient.HTTPClient>`

    :raises ValueError: if ``priority_list`` is not a :class:`str <python:str>`

    """
    priority_list = validators.string(priority_list, allow_empty = False)
    priorities = priority_list.split('|')

    if priorities[-1:] != 'UrllibClient':
        priorities.append('UrllibClient')

    for item in priorities:
        is_third_party = '.' in item
        client = get_http_client(item, is_third_party = is_third_party)

        if client is not None:
            return client


__all__ = [
    'get_http_client',
    'default_http_client',
    'HTTPClient',
    'HTTPResponse',
]
