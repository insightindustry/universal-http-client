# -*- coding: utf-8 -*-

"""
##############################################
universal_http_client.ext.UrlFetchClient
##############################################

Implements support for the :doc:`urlfetch <urlfetch:index>` :term:`HTTP Library`.

.. warning::

  This :term:`HTTP Client` should *not* be confused for the :class:`GAEUrlFetchClient`
  which implements support for the Google App Engine
  `urlfetch <https://cloud.google.com/appengine/docs/standard/python/refdocs/google.appengine.api.urlfetch>`_
  HTTP library.

"""
import warnings

from validator_collection import validators, checkers

from universal_http_client.HTTPClient import HTTPClient
from universal_http_client.HTTPResponse import HTTPResponse
from universal_http_client import errors

import urlfetch

class UrlFetchClient(HTTPClient):
    """class:`HTTPClient` for the :doc:`urlfetch <urlfetch:index>` library.

    .. warning::

      This :term:`HTTP Client` should *not* be confused for the :class:`GAEUrlFetchClient`
      which implements support for the Google App Engine
      `urlfetch <https://cloud.google.com/appengine/docs/standard/python/refdocs/google.appengine.api.urlfetch>`_
      HTTP library.

    """

    name = "urlfetch"

    def __init__(self,
                 timeout = None,
                 max_redirects = 0,
                 length_limit = None,
                 random_user_agent = False,
                 **kwargs):
        """

        .. seealso::

          Parameters for :class:`HTTPClient`.

        :param timeout: Sets the maximum time to wait for an HTTP response
          before the urlfetch library times out. Defaults to
          :obj:`None <python:None>`.
        :type timeout: :class:`float <python:float>` / :obj:`None <python:None>`

        :param max_redirects: The maximum number of redirect responses to
          automatically follow. Defaults to ``0``, which essentially disables
          automatic following of any redirect responses.
        :type max_redirects: :class:`int <python:int>`

        :param length_limit: The maximum number of bytes to receive. If a
          response exceeds the limit specified, will raise a
          :class:`ResponseError <universal_http_client.errors.ResponseError>`.
          If :obj:`None <python:None>`, no limit will be imposed. Defaults to
          :obj:`None <python:None>`.
        :type length_limit: :class:`int <python:int>`

        :param random_user_agent: If ``True``, will generate a random user-agent
          to supply with requests. If ``False``, will use
          ``urlfetch/<URLFETCH VERSION NUMBER>`` as the user-agent. Defaults to
          ``False``.
        :type random_user_agent: :class:`bool <python:bool>`

        :param kwargs: Additional keyword arguments that will be passed to the
          :doc:`urlfetch <urlfetch:index>` library when executing a request.

        :returns: An :class:`HTTPClient` instance designed to wrap the
          :doc:`urlfetch <urlfetch:index>` library.
        :rtype: :class:`UrlFetchClient` (inherits from :class:`HTTPClient`)

        """
        self._timeout = None
        self._max_redirects = 0
        self._length_limit = None
        self._random_user_agent = False

        super(UrlFetchClient, self).__init__(**kwargs)

        self.timeout = timeout
        self.max_redirects = max_redirects
        self.length_limit = length_limit
        self.random_user_agent = random_user_agent

    @property
    def timeout(self):
        """The maximum time to wait for an HTTP response before the HTTP library
        times out.

        :rtype: :class:`int <python:int>`
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = validators.integer(value,
                                           allow_empty = True,
                                           minimum = 0)

    @property
    def max_redirects(self):
        """The maximum number of redirects to automatically follow.

        :rtype: :class:`int <python:int>`
        """
        return self._max_redirects

    @max_redirects.setter
    def max_redirects(self, value):
        if value is None:
            value = 0

        self._max_redirects = validators.integer(value,
                                                 allow_empty = False,
                                                 minimum = 0)

    @property
    def length_limit(self):
        """The maximum number of bytes to return in the response.

        If :obj:`None <python:None>`, no limit will be applied.

        :rtype: :class:`int <python:int>`
        """
        return self._length_limit

    @length_limit.setter
    def length_limit(self, value):
        self._length_limit = validators.integer(value,
                                                allow_empty = True,
                                                minimum = 0)

    @property
    def random_user_agent(self):
        """If ``True``, will generate a random user-agent to supply with
        requests.

        If ``False``, will use ``urlfetch/<URLFETCH VERSION NUMBER>`` as the
        user-agent.

        :rtype: class:`bool <python:bool>`
        """
        return self._random_user_agent

    @random_user_agent.setter
    def random_user_agent(self, value):
        self._random_user_agent = bool(value)

    def _request(self,
                 method,
                 url,
                 parameters = None,
                 headers = None,
                 request_body = None,
                 **kwargs):
        timeout = kwargs.pop('timeout', self.deadline)
        max_redirects = kwargs.pop('follow_redirects', self.follow_redirects)
        length_limit = kwargs.pop('length_limit', self.length_limit)
        random_user_agent = kwargs.pop('random_user_agent', self.random_user_agent)

        timeout = validators.integer(timeout,
                                     allow_empty = True,
                                     minimum = 0)
        max_redirects = validators.integer(max_redirects,
                                           allow_empty = False,
                                           minimum = 0)
        length_limit = validators.integer(length_limit,
                                          allow_empty = True,
                                          minimum = 0)
        random_user_agent = bool(random_user_agent)

        try:
            result = urlfetch.request(
                url = url,
                method = method,
                params = parameters,
                headers = headers,
                data = request_body,
                timeout = timeout,
                max_redirects = max_redirects,
                limit_length = limit_length,
                randua = random_user_agent,
                proxies = self.proxy,
                **kwargs
            )
        except urlfetch.InvalidURLError:
            raise errors.InvalidURLError(
                "The URL requested (%s) was empty or invalid." % url
            )
        except urlfetch.TooManyRedirectsError:
            raise errors.ResponseError(
                "The redirect limit configured in the request or set by default "
                "(%s) was reached before a response was returned." % max_redirects
            )
        except urlfetch.Timeout:
            raise errors.TimeoutError(
                "The connection timeout (%d) was exceeded." % timeout
            )
        except urlfetch.ContentLimitExceeded:
            raise errors.ResponseError(
                "The response exceeded the content limit (%d bytes)." % length_limit
            )
        except urlfetch.ContentDecodingError:
            raise errors.ResponseError(
                "Error when decoding content in the response."
            )
        except urlfetch.UrlfetchException as error:
            raise errors.HTTPLibraryError(
                "The Urlfetch library generated an error for an indeterminate "
                "reason."
            )

        cookies = result.cookies
        cookiejar = None
        if cookies:
            cookiejar = CookieJar()
            for cookie in result.cookies:
                cookiejar.set_cookie(cookie)

        response = HTTPResponse(content = result.content,
                                status_code = result.status_code,
                                headers = result.headers,
                                cookies = cookiejar)

        return response, response.status_code

    def close(self):
        pass
