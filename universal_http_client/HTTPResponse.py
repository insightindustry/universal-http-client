# -*- coding: utf-8 -*-

"""
#########################################
universal_http_client.HTTPResponse
#########################################

Implements a standardized interface for managing response data returned from
an :class:`HTTPClient` instance.

"""
from universal_http_client._compat import str, CookieJar, Cookie

from validator_collection import validators, checkers

class HTTPResponse(object):
    """A Python object representation of the response returned from an HTTP
    Server in answer to an HTTP request."""

    def __init__(self,
                 content = None,
                 status_code = None,
                 headers = None,
                 cookies = None,
                 **kwargs):
        """
        :param content: The content returned from the HTTP Server. Defaults to
          :obj:`None <python:None>`.
        :type content: :class:`bytes <python:bytes>`

        :param status_code: The HTTP Status Code returned from the HTTP Server.
          Defaults to :obj:`None <python:None>`.
        :type status_code: :class:`int <python:int>` / :obj:`None <python:None>`

        :param headers: The HTTP headers returned with the response from the
          HTTP Server. Represented as a :class:`dict <python:dict>` where the
          header name is the key and the value of the header item is the value.
          Defaults to :obj:`None <python:None>`
        :type headers: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param cookies: A :class:`CookieJar <python:http.cookiejar.CookieJar>`
          of :class:`Cookies <python:http.cookiejar.Cookie>` returned with the
          response. Defaults to :obj:`None <python:None>`
        :type cookies: :class:`CookieJar <python:http.cookiejar.CookieJar>` /
          :obj:`None <python:None>`

        :rtype: :class:`HTTPResponse`

        """
        self._content = None
        self._status_code = None
        self._headers = None
        self._cookies = None

        self.content = content
        self.status_code = status_code
        self.headers = headers
        self.cookies = cookies

    @property
    def status_code(self):
        """The :term:`HTTP Status Code` returned by the HTTP Server.

        :rtype: :class:`int <python:int>` / :obj:`None <python:None>`
        """
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = validators.integer(value,
                                               allow_empty = True,
                                               minimum = 0)

    @property
    def headers(self):
        """The :term:`HTTP Headers` returned by the HTTP Server.

        .. warning::

          The ``headers`` :class:`dict <python:dict>` stores all header names
          in *lowercase* by default. You can either reference them directly
          through the ``headers`` property by looking for lowercase values, or
          you can use the
          :meth:`get_header() <universal_http_client.HTTPResponse.HTTPResponse.get_header>`
          method.

        :rtype: :class:`dict <python:dict>` / :obj:`None <python:None>`
        """
        return self._headers

    @headers.setter
    def headers(self, value):
        value = validators.dict(value, allow_empty = True)
        new_value = None
        if value:
            new_value = { x.lower(): value[x] for x in value }

        self._headers = new_value

    @property
    def content(self):
        """The content returned from the HTTP Server in response to the HTTP
        request.

        :rtype; :class:`bytes <python:bytes>` / :obj:`None <python:None>`
        """
        return self._content

    @content.setter
    def content(self, value):
        if not value:
            self._content = None
        elif checkers.is_string(value, allow_empty = False):
            self._content = value.encode('utf-8')
        elif checkers.is_type(value, ('bytes', 'bytearray')):
            self._content = value
        else:
            raise ValueError('HTTP response content cannot be converted to bytesarray')

    @property
    def cookies(self):
        """A :class:`CookieJar <python:http.cookiejar.CookieJar>` of
        :class:`Cookie <python:http.cookiejar.Cookie>` instances returned with
        the HTTP response.

        :rtype: :class: `CookieJar <python:http.cookiejar.CookieJar>` /
          :obj:`None <python:None>`
        """
        return self._cookies

    @cookies.setter
    def cookies(self, value):
        if not value:
            self._cookies = None
        elif isinstance(value, CookieJar):
            self._cookies = value
        else:
            raise ValueError('cookies expects a CookieJar, but received a '
                             '%s' % value.__class__.__name__)

    @property
    def content_type(self):
        """The MIME content type of the HTTP response as supplied in the HTTP header.

        :rtype: :class:`str <python:str>` / :obj:`None <python:None>`
        """
        if self.headers:
            return self.headers.get('content-type', None)

        return None

    @property
    def text(self):
        """A :class:`str <python:str>` representation of the HTTP response content.

        :rtype: :class:`str <python:str>` / :obj:`None <python:None>`
        """
        value = self.content
        if not value:
            return None
        return self.content.decode('utf-8')

    @property
    def json(self):
        """Returns a deserialized (:class:`dict <python:dict>`) version of the
        response content if the content type is JSON. Otherwise, returns
        :obj:`None <python:None>`.

        :rtype: :class:`dict <python:dict>` / :obj:`None <python:None>`
        """
        if 'json' in self.content_type:
            return validators.json(self.text, allow_empty = True)

        return None

    def get_header(self,
                   header,
                   default = None):
        """Retrieve the HTTP header value indicated by ``header``.

        :param header: The header to retrieve. Case insensitive.
        :type header: :class:`str <python:str>`

        :param default: The default value to return for the header if it is not
          found. Defaults to :obj:`None <python:None>`.

        :returns: The header value or the default value if no header value found.
        :rtype: :class:`str <python:str>` / any time

        :raises ValueError: if ``header`` is not a :class:`str <python:str>`

        """
        header = validators.string(header, allow_empty = None)
        header = header.lower()

        return self.headers.get(header, default)
