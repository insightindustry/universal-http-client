# -*- coding: utf-8 -*-

"""
#########################################
universal_http_client.HTTPClient
#########################################

Implements a standardized interface for requesting URLs from the internet and
returning the response.

"""
import threading

from backoff_utils import backoff
from backoff_utils import strategies as backoff_strategies
from validator_collection import validators

from universal_http_client.utilities import CA_BUNDLE_PATH, to_utf8, HTTP_METHODS
from universal_http_client.errors import check_for_errors, HTTPTimeoutError


class HTTPClient(object):                                                                 # pylint: disable=R0205
    """Base class that provides HTTP connectivity."""

    def __init__(self,
                 verify_ssl_certs = True,
                 proxy = None,
                 max_retries = None,
                 retry_strategy = backoff_strategies.Exponential,
                 status_code_mapping = None):
        """
        :param verify_ssl_certs: If ``True``, will verify SSL certificates. If
          ``False``, will not verify SSL certificates. Defaults to ``True``.
        :type verify_ssl_certs: :class:`bool <python:bool>`

        :param proxy: The (optional) configuration of proxy servers to use when
          executing HTTP requests. Accepts either a single URL as a string or a
          :class:`dict <python:dict>` with ``https`` and/or ``http`` keys where
          each value is a URL expressed as a :class:`str <python:str>`. Defaults
          to :obj:`None <python:None>`.
        :type proxy: :class:`str <python:str>` / :class:`dict <python:dict>` /
          :obj:`None <python:None>`

        :param max_retries: The maximum number of retry attempts to make if the
          HTTP response returns a retryable error. If :obj:`None <python:None>`,
          will default to the value of the ``BACKOFF_DEFAULT_TRIES`` environment
          variable. If set to ``0``, will not attempt any retries. Defaults to
          :obj:`None <python:None>`.
        :type max_retries: :class:`int <python:int>` / :obj:`None <python:None>`

        :param max_delay: The maximum amount of time (expressed in seconds) to
          wait before giving up once and for all. If :obj:`None <python:None>`,
          will apply the ``BACKOFF_DEFAULT_DELAY`` environment variable. Defaults
          to :obj:`None <python:None>`.
        :type max_delay: :class:`int <python:int>` / :obj:`None <python:None>`

        :param retry_strategy: The
          :term:`Backoff Strategy <backoff:Backoff Strategy>` to use when retrying
          a recoverable-but-failed HTTP request. Defaults to
          :class:`Exponential <backoff:backoff_utils.strategies.Exponential>`.
          If set to :obj:`None <python:None>`, will disable the retrying of failed
          requests.
        :type retry_strategy: :class:`BackoffStrategy <backoff:backoff_utils.strategies.BackoffStrategy>` / :obj:`None <python:None>`

        :param status_code_mapping: Configures how HTTP status codes map to
          exceptions that should be raised when checking for errors. Expects
          a :class:`dict <python:dict>` where keys are HTTP status codes and
          values are either :class:`Exception <python:Exception>` classes or
          strings with names of :doc:`Universal HTTP Client errors <errors>`.
          if :obj:`None <python:None>` will apply the
          :ref:`default status code mapping <default_status_code_mapping>`.
          Defaults to :obj:`None <python:None>`.
        :type status_code_mapping: :class:`dict <python:dict>` /
          :obj:`None <python:None>`

        :returns: An :class:`HTTPClient` instance.
        :rtype: :class:`HTTPClient`

        :raises ValueError: if ``proxy`` is not an acceptable type
        :raises InvalidURLError: if ``proxy`` or a value in ``proxy`` is not a
          valid URL

        """
        self._verify_ssl_certs = None
        self._proxy = None
        self._thread_local = threading.local()
        self._max_retries = None
        self._max_delay = None
        self._retry_strategy = None
        self._status_code_mapping = None

        self.verify_ssl_certs = verify_ssl_certs
        self.proxy = proxy

        self.max_retries = max_retries
        self.max_delay = max_delay
        self.retry_strategy = retry_strategy
        self.status_code_mapping = status_code_mapping

    @property
    def verify_ssl_certs(self):
        """Indicates whether the :term:`HTTP Client` should verify SSL
        certificates when executing SSL requests.

        :returns: ``True`` if certificates should be verified, ``False`` if not
        :rtype: :class:`bool <python:bool>`
        """
        return self._verify_ssl_certs

    @verify_ssl_certs.setter
    def verify_ssl_certs(self, value):
        self._verify_ssl_certs = bool(value)

    @property
    def proxy(self):
        """The URL(s) to use as proxy servers when executing HTTP requests.

        :returns: A :class:`dict <python:dict>` with keys ``https`` and ``http``
          whose values are either the URL to use as a proxy server when executing
          a request using that protocol or :obj:`None <python:None>` if no proxy
          is to be used.
        :rtype: :class:`dict <python:dict>` with keys ``https`` and ``http`` whose
          values are either :class:`str <python:str>` or :obj:`None <python:None>`.
        """
        if not self._proxy:
            return {
                'https': None,
                'http': None
            }

        return self._proxy

    @proxy.setter
    def proxy(self, value):
        if checkers.is_dict(value):
            if 'https' not in value and 'http' not in value:
                raise ValueError('proxy supplied as dict did not contain keys '
                                 '"https" and "http"')
            https = value.get('https', None)
            http = value.get('http', None)
        elif value is not None:
            https = value
            http = value
        else:
            https = None
            http = None

        https = validators.url(https, allow_empty = True)
        http = validators.url(http, allow_empty = True)

        self._proxy = {
            'https': https,
            'http': http
        }

    @property
    def max_retries(self):
        """The maximum number of retry attempts to make if a recoverable error
        occurred.

        .. note::

          If this property is set to :obj:`None <python:None>`, will apply and
          return the same value as the ``BACKOFF_DEFAULT_TRIES`` environment
          variable. If that value is not set, will return ``0``  (effectively
          disabling retries).

        :rtype: :class:`int <python:int>`
        """
        if self._max_retries is None:
            return os.getenv('BACKOFF_DEFAULT_TRIES', 0)

        return self._max_retries

    @max_retries.setter
    def max_retries(self, value):
        value = validators.integer(value,
                                   allow_empty = True,
                                   minimum = 0)
        self._max_retries = value

    @property
    def max_delay(self):
        """The number of seconds to continue retrying a recoverable request
        before giving up.

        .. note::

          If this property is set to :obj:`None <python:None>`, will apply and
          return the same value as the ``BACKOFF_DEFAULT_DELAY`` environment
          variable. If that value is not set, will return ``0`` (effectively
          disabling retries).

        :rtype: :class:`int <python:int>`

        """
        if self._max_delay is None:
            return os.getenv('BACKOFF_DEFAULT_DELAY', 0)

        return self._max_delay

    @property
    def retry_strategy(self):
        """The :term:`backoff strategy <backoff:Backoff Strategy>` to apply
        when retrying a failed-but-recoverable HTTP request.

        .. note::

          If this property is set to :obj:`None <python:None>`, will effectively
          disable all retries.

        :rtype: :class:`backoff_utils.strategies.BackoffStrategy <backoff:backoff_utils.strategies.BackoffStrategy>`
        """
        return self._retry_strategy

    @retry_strategy.setter
    def retry_strategy(self, value):
        if value is None:
            self._retry_strategy = None
        elif checkers.is_type(value, 'BackoffStrategy'):
            self._retry_strategy = value
        else:
            raise ValueError('retry_strategy must either be None or a valid BackoffStrategy subclass')

    @property
    def _disable_retries(self):
        """Indicates whether retries should be disabled (``True``) or enabled
        (``False``).

        :rtype: :class:`bool <python:bool>`
        """
        return self.retry_strategy is not None and \
               self.max_retries > 0 and \
               self.max_delay > 0

    @property
    def status_code_mapping(self):
        """The mapping between HTTP Status Codes and errors to be raised by
        the Universal HTTP Client's native
        :func:`check_for_errors() <universal_http_client.errors.check_for_errors>`
        feature. If

        :returns: A :class:`dict <python:dict>` whose keys are HTTP status codes
          (:class:`int <python:int>`) and whose values are either
          :class:`Exceptions <python:Exception>` to raise or the names of
          :doc:`Universal HTTP Client errors <errors>`. A value of
          :obj:`None <python:None>` indicates that the
          :ref:`default status code mapping <default_status_code_mapping>` should
          be used.
        :rtype: :class:`dict <python:dict>` / :obj:`None <python:None>`
        """
        return self._status_code_mapping

    @status_code_mapping.setter
    def status_code_mapping(self, value):
        value = validators.dict(value, allow_empty = True)
        if value:
            [validators.integer(x,
                                allow_empty = False,
                                minimum = 0)
             for x in value.keys()]

        self._status_code_mapping = value

    def configure(self,
                  verify_ssl_certs = True,
                  proxy = None,
                  max_retries = None,
                  max_delay = None,
                  retry_strategy = backoff_strategies.Exponential,
                  status_code_mapping = None):
        """Configures the :class:`HTTPClient` instance.

        :param verify_ssl_certs: If ``True``, will verify SSL certificates on
          requests. If ``False``, will not verify SSL certificates. Defaults to
          ``True``.
        :type verify_ssl_certs: :class:`bool <python:bool>`

        :param proxy: The (optional) configuration of proxy servers to use when
          executing HTTP requests. Accepts either a single URL as a string or a
          :class:`dict <python:dict>` with ``https`` and/or ``http`` keys where
          each value is a URL expressed as a :class:`str <python:str>`. Defaults
          to :obj:`None <python:None>`.
        :type proxy: :class:`str <python:str>` / :class:`dict <python:dict>` /
          :obj:`None <python:None>`

        :param max_retries: The maximum number of retry attempts to make if the
          HTTP response returns a retryable error. If :obj:`None <python:None>`,
          will default to the value of the ``BACKOFF_DEFAULT_TRIES`` environment
          variable. If set to ``0``, will not attempt any retries. Defaults to
          :obj:`None <python:None>`.
        :type max_retries: :class:`int <python:int>` / :obj:`None <python:None>`

        :param max_delay: The maximum amount of time (expressed in seconds) to
          wait before giving up once and for all. If :obj:`None <python:None>`,
          will apply the ``BACKOFF_DEFAULT_DELAY`` environment variable. Defaults
          to :obj:`None <python:None>`.
        :type max_delay: :class:`int <python:int>` / :obj:`None <python:None>`

        :param retry_strategy: The
          :term:`Backoff Strategy <backoff:Backoff Strategy>` to use when retrying
          a recoverable-but-failed HTTP request. Defaults to
          :class:`Exponential <backoff:backoff_utils.strategies.Exponential>`.
          If set to :obj:`None <python:None>`, will disable the retrying of failed
          requests.
        :type retry_strategy: :class:`BackoffStrategy <backoff:backoff_utils.strategies.BackoffStrategy>` / :obj:`None <python:None>`

        :param status_code_mapping: Configures how HTTP status codes map to
          exceptions that should be raised when checking for errors. Expects
          a :class:`dict <python:dict>` where keys are HTTP status codes and
          values are either :class:`Exception <python:Exception>` classes or
          strings with names of :doc:`Universal HTTP Client errors <errors>`.
          if :obj:`None <python:None>` will apply the
          :ref:`default status code mapping <default_status_code_mapping>`.
          Defaults to :obj:`None <python:None>`.
        :type status_code_mapping: :class:`dict <python:dict>` /
          :obj:`None <python:None>`

        """
        self.verify_ssl_certs = verify_ssl_certs
        self.proxy = proxy

        self.max_retries = max_retries
        self.max_delay = max_delay
        self.retry_strategy = retry_strategy

        self.status_code_mapping = status_code_mapping

    def _request(self,
                 method,
                 url,
                 parameters = None,
                 headers = None,
                 request_body = None,
                 **kwargs):
        """Execute a standard HTTP request.

        :param method: The HTTP method to use for the request. Accepts `GET`, `HEAD`,
          `POST`, `PATCH`, `PUT`, `DELETE`, or `OPTIONS`.
        :type method: :class:`str <python:str>`

        :param url: The URL to execute the request against.
        :type url: :class:`str <python:str>`

        :param parameters: URL parameters to submit with the request. Defaults to
          :obj:`None <python:None>`.
        :type parameters: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param headers: HTTP headers to submit with the request. Defaults to
          :obj:`None <python:None>`.
        :type headers: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param request_body: The data to supply in the body of the request. Defaults to
          :obj:`None <python:None>`.
        :type request_body: :obj:`None <python:None>` / :class:`dict <python:dict>` /
          :class:`str <python:str>` / :class:`bytes <python:bytes>`

        :param kwargs: Additional keyword arguments that can be leveraged by the
          underlying :term:`HTTP Library`.

        :returns: The content of the HTTP response and the status code of the
          HTTP response.
        :rtype: :class:`tuple <python:tuple>` of
          :class:`HTTPResponse <python:universal_http_client.HTTPResponse.HTTPResponse>`
          and :class:`int <python:int>`

        :raises ValueError: if ``method`` is not either ``GET``, ``HEAD``, ``POST``,
          ``PATCH``, ``PUT``, ``DELETE``, or ``OPTIONS``
        :raises ValueError: if ``url`` is not a valid URL
        :raises HTTPTimeoutError: if the request times out
        :raises SSLError: if the request fails SSL certificate verification

        """
        raise NotImplementedError(
            "HTTPClient subclasses must implement `_request`"
        )

    def request(self,
                method,
                url,
                parameters = None,
                headers = None,
                request_body = None,
                check_for_errors = True,
                disable_retries = False,
                **kwargs):
        """Execute a standard HTTP request.

        :param method: The HTTP method to use for the request. Accepts `GET`, `HEAD`,
          `POST`, `PATCH`, `PUT`, or `DELETE`.
        :type method: :class:`str <python:str>`

        :param url: The URL to execute the request against.
        :type url: :class:`str <python:str>`

        :param parameters: URL parameters to submit with the request. Defaults to
          :obj:`None <python:None>`.
        :type parameters: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param headers: HTTP headers to submit with the request. Defaults to
          :obj:`None <python:None>`.
        :type headers: :class:`dict <python:dict>` / :obj:`None <python:None>`

        :param request_body: The data to supply in the body of the request. Defaults to
          :obj:`None <python:None>`.
        :type request_body: :obj:`None <python:None>` / :class:`dict <python:dict>` /
          :class:`str <python:str>` / :class:`bytes <python:bytes>`

        :param check_for_errors: If ``True``, will evaluate the status code
          returned and raise an :class:`Exception <python:Exception>` if
          appropriate as per the
          :attribute:`.status_code_mapping <universal_http_client.HTTPClient.status_code_mapping>`
          configured. If ``False`` will not check the HTTP status code for an error.
          Defaults to ``True``.
        :type check_for_errors: :class:`bool <python:bool>`

        :param disable_retries: If ``True``, will disable all retries without
          overriding the configuration set for the HTTP client instance. If
          ``False``, will apply the retry configuration set for the HTTP client
          instance. Defaults to ``False``.
        :type disable_retries: :class:`bool <python:bool>`

        :param verify_ssl_certs: If ``True``, will verify SSL certificates *for
          this request*. If ``False``, will not verify SSL certificates
          *for this request*. By default, applies the configuration applied to
          the HTTP client.
        :type verify_ssl_certs: :class:`bool <python:bool>`

        :param proxy: The (optional) configuration of proxy servers to use
          *for this request*. Accepts either a single URL as a string or a
          :class:`dict <python:dict>` with ``https`` and/or ``http`` keys where
          each value is a URL expressed as a :class:`str <python:str>`. By default,
          applies the configuration applied to the HTTP client.
        :type proxy: :class:`str <python:str>` / :class:`dict <python:dict>` /
          :obj:`None <python:None>`

        :param max_retries: The maximum number of retry attempts to make if the
          HTTP response returns a retryable error. By default, applies the
          configuration applied to the HTTP client.
        :type max_retries: :class:`int <python:int>` / :obj:`None <python:None>`

        :param max_delay: The maximum amount of time (expressed in seconds) to
          wait before giving up once and for all. By default, applies the
          configuration applied to the HTTP client.
        :type max_delay: :class:`int <python:int>`

        :param retry_strategy: The
          :term:`Backoff Strategy <backoff:Backoff Strategy>` to use when retrying
          *this* request. By default, applies the configuration applied to the
          HTTP client.
        :type retry_strategy: :class:`BackoffStrategy <backoff:backoff_utils.strategies.BackoffStrategy>`

        :param status_code_mapping: Configures how HTTP status codes map to
          exceptions that should be raised when checking for errors. Expects
          a :class:`dict <python:dict>` where keys are HTTP status codes and
          values are either :class:`Exception <python:Exception>` classes or
          strings with names of :doc:`Universal HTTP Client errors <errors>`.
          By default, applies the configuration applied to the HTTP client.
        :type status_code_mapping: :class:`dict <python:dict>`

        :param kwargs: Additional keyword arguments that can be leveraged by the
          underlying :term:`HTTP Library`.

        :returns: The content of the HTTP response, the status code of the HTTP response,
          and the headers of the HTTP response.
        :rtype: :class:`tuple <python:tuple>` of :class:`bytes <python:bytes>`,
          :class:`int <python:int>`, and :class:`dict <python:dict>`

        :raises ValueError: if ``method`` is not either ``GET``, ``HEAD``, ``POST``,
          ``PATCH``, ``PUT`` or ``DELETE``
        :raises ValueError: if ``url`` is not a valid URL
        :raises ValueError: if ``headers`` is not empty and is not a
          :class:`dict <python:dict>`

        :raises HTTPTimeoutError: if the request times out
        :raises SSLError: if the request fails SSL certificate verification
        :raises WalkScoreError: *or sub-classes* for other errors returned by the API

        """
        method = validators.string(method, allow_empty = False)
        method = method.upper()
        if method not in HTTP_METHODS:
            raise ValueError('method (%s) not a recognized HTTP method' % method)

        url = validators.url(url, allow_empty = False)

        parameters = validators.dict(parameters, allow_empty = True)
        headers = validators.dict(headers, allow_empty = True)

        verify_ssl_certs = kwargs.pop(verify_ssl_certs, self.verify_ssl_certs)
        proxy = kwargs.pop(proxy, self.proxy)

        if not disable_retries:
            max_retries = kwargs.pop(max_retries, self.max_retries)
            max_delay = kwargs.pop(max_delay, self.max_delay)
            retry_strategy = kwargs.pop(retry_strategy, self.retry_strategy)
        else:
            max_retries = 0
            max_delay = 0
            retry_strategy = None

        verify_ssl_certs = bool(verify_ssl_certs)
        proxy = validators.dict(proxy, allow_empty = False)
        proxy['https'] = validators.url(proxy['https'], allow_empty = True)
        proxy['http'] = validators.url(proxy['http'], allow_empty = True)

        if not disable_retries:
            max_retries = validators.integer(max_retries,
                                             allow_empty = False,
                                             minimum = 0)
            max_delay = validators.integer(max_delay,
                                           allow_empty = False,
                                           minimum = 0)
            if retry_strategy:
                if not checkers.is_type(retry_strategy, 'BackoffStrategy'):
                    raise ValueError('retry_strategy must either be None or a '
                                     'valid BackoffStrategy subclass')

            if max_retries = 0 or max_delay = 0 or retry_strategy is None:
                disable_retries = True

        if check_for_errors:
            status_code_mapping = kwargs.pop(status_code_mapping,
                                             self.status_code_mapping)

            status_code_mapping = validators.dict(status_code_mapping,
                                                  allow_empty = True)
            if status_code_mapping:
                [validators.integer(x) for x in status_code_mapping.keys()]

        if disable_retries:
            response, status_code = self._request(method,
                                                  url,
                                                  parameters,
                                                  headers,
                                                  request_body,
                                                  **kwargs)
        else:
            response, status_code = backoff(self.request,
                                            args = [method, url, parameters, headers, request_body],
                                            kwargs = kwargs,
                                            catch_exceptions = [type(HTTPTimeoutError)],
                                            strategy = retry_strategy)

        if check_for_errors:
            check_for_errors_(status_code,
                              response,
                              status_code_mapping = status_code_mapping)

        return response, status_code

    def close(self):
        """Closes an existing HTTP connection/session."""

        raise NotImplementedError(
            "HTTPClient subclasses must implement `close`"
        )
