# -*- coding: utf-8 -*-

"""
##############################################
universal_http_client.ext.GAEUrlFetchClient
##############################################

Implements support for the Google App Engine
`urlfetch <https://cloud.google.com/appengine/docs/standard/python/refdocs/google.appengine.api.urlfetch>`_
:term:`HTTP Library`.

.. warning::

  This :term:`HTTP Client` should *not* be confused for the :class:`UrlFetchClient`
  which implements support for the generic :doc:`urlfetch <urlfetch:index>`
  HTTP library.

"""
import warnings

from validator_collection import validators, checkers

from universal_http_client.HTTPClient import HTTPClient
from universal_http_client.HTTPResponse import HTTPResponse
from universal_http_client import errors

from google.appengine.api import urlfetch

class GAEUrlFetchClient(HTTPClient):
    """class:`HTTPClient` for the Google App Engine `urlfetch <https://cloud.google.com/appengine/docs/standard/python/refdocs/google.appengine.api.urlfetch>`_
    library.

    .. warning::

      This :term:`HTTP Client` should *not* be confused for the :class:`UrlFetchClient`
      which implements support for the generic :doc:`urlfetch <urlfetch:index>`
      HTTP library.

    """

    name = "gae_urlfetch"

    def __init__(self,
                 deadline = 55,
                 follow_redirects = True,
                 **kwargs):
        """
        :param deadline: Sets the maximum time to wait for an HTTP response
          before the GAE urlfetch library times out. Defaults to ``55``.

          .. tip::

            GAE requests time out after 60 seconds, so make sure to default to
            a value approaching 60s to allow for a slow HTTP response.
        :type deadline: :class:`int <python:int>`

        :param follow_redirects: If ``True``, redirects are transparently
          followed, and the response (if less than 5 redirects) contains the
          final destination’s payload with a status code of `200`. You lose,
          however, the redirect chain information. If set to ``False``, you see
          the HTTP response, including the `Location` header, and redirects are
          not automatically followed. Defaults to ``True``.
        :type follow_redirects: :class:`bool <python:bool>`

        :returns: An :class:`HTTPClient` instance designed to wrap the Google
          App Engine `urlfetch <https://cloud.google.com/appengine/docs/standard/python/refdocs/google.appengine.api.urlfetch>`_
          module.
        :rtype: :class:`GAEUrlFetchClient` (inherits from :class:`HTTPClient`)

        """
        self._deadline = None
        self._follow_redirects = True

        super(GAEUrlFetchClient, self).__init__(**kwargs)

        self.deadline = deadline
        self.follow_redirects = follow_redirects

    @property
    def deadline(self):
        """The maximum time to wait for an HTTP response before the HTTP library
        times out.

        :rtype: :class:`int <python:int>`
        """
        return self._deadline

    @deadline.setter
    def deadline(self, value):
        self._deadline = validators.integer(value,
                                            allow_empty = True,
                                            minimum = 0,
                                            maximum = 60)

    @property
    def follow_redirects(self):
        """Determines whether to automatically follow redirects returned as a
        response.

        If ``True``, redirects are transparently and automatically followed,
        and the response (if less than 5 redirects) contains the final
        destination’s payload with a status code of `200`. You lose,
        however, the redirect chain information.

        If ``False``, you see the HTTP response, including the `Location`
        header, and redirects are *not* automatically followed.

        :rtype: :class:`bool <python:bool>`
        """
        return self._follow_redirects

    @follow_redirects.setter
    def follow_redirects(self, value):
        self._follow_redirects = bool(value)

    def _request(self,
                 method,
                 url,
                 parameters = None,
                 headers = None,
                 request_body = None,
                 **kwargs):
        deadline = kwargs.pop('deadline', self.deadline)
        follow_redirects = kwargs.pop('follow_redirects', self.follow_redirects)

        deadline = validators.integer(deadline,
                                      allow_empty = False,
                                      minimum = 0,
                                      maximum = 60)
        follow_redirects = bool(follow_redirects)
        allow_truncated = kwargs.pop('allow_truncated', True)

        try:
            result = urlfetch.request(
                url = url,
                method = method,
                params = parameters,
                headers = headers,
                validate_certificate = self.verify_ssl_certs,
                deadline = deadline,
                follow_redirects = follow_redirects,
                allow_truncated = True,
                data = request_body,
                **kwargs
            )
        except urlfetch.PayloadTooLargeError:
            raise errors.InvalidRequestError(
                "The request payload exceeds the limit imposed by Google App "
                "Engine."
            )
        except urlfetch.InvalidURLError:
            raise errors.InvalidURLError(
                "The URL requested (%s) was empty or invalid."
                "Google App Engine only supports HTTP and HTTPS URLs, with "
                "a maximum URL length of 2048 characters, and no login / "
                "password portion. In deployed applications, only ports 80 "
                "and 443 for HTTP and HTTPS respectively are allowed." % url
            )
        except urlfetch.MalformedReplyError:
            raise errors.ResponseError(
                "The target server returned an invalid HTTP response."
            )
        except urlfetch.TooManyRedirectsError:
            raise errors.ResponseError(
                "The redirect limit configured in the request (or set by "
                "default) was reached before a response was returned."
            )
        except urlfetch.DNSLookupFailedError:
            raise errors.InvalidURLError(
                "DNS lookup for the URL (%s) failed." % url
            )
        except urlfetch.DeadlineExceededError:
            raise errors.TimeoutError(
                "The connection timeout (%d) was exceeded. Using urlfetch, "
                "this defaults to 55 seconds due to a hard timeout of 60s "
                "imposed by Google App Engine." % deadline
            )
        except urlfetch.DownloadError:
            raise errors.ConnectionError(
                "The URL could not be retrieved. This exception is only raised "
                "when it is impossible to contact the underlying server."
            )
        except urlfetch.ResponseTooLargeError:
            warnings.warn("The response was too large and was therefore truncated.",
                          errors.ResponseWarning)
        except urlfetch.SSLCertificateError:
            raise errors.SSLCertificateError(
                "An invalid server certificate was presented."
            )

        response = HTTPResponse(content = result.content,
                                status_code = result.status_code,
                                headers = result.headers)

        return response, response.status_code

    def close(self):
        pass
