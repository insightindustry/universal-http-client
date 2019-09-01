# -*- coding: utf-8 -*-

"""
##############################################
universal_http_client.ext.UrllibClient
##############################################

Implements support for the :doc:`urllib <python:urllib>` and
:doc:`urllib2 <python27:urllib2>` :term:`HTTP Libraries <HTTP Library>`.


"""
import warnings

from validator_collection import validators, checkers

from universal_http_client.HTTPClient import HTTPClient
from universal_http_client.HTTPResponse import HTTPResponse
from universal_http_client import errors

try:
    import urllib2 as urllib
except ImportError:
    import urllib

def _validate_files(files):
    """Validate that a ``files`` parameter matches the structure expected by the
    requests library.

    :returns: A requests-compatible ``files`` parameter.
    :rtype: :class:`dict <python:dict>` / :obj:`None <python:None>`
    """
    value = validators.dict(value, allow_empty = True)
    if value:
        for key in value:
            if not checkers.is_string(key):
                raise errors.RequestError(
                    "Keys in the files parameter must be strings. "
                    "Found %s." % key.__class__.__name__
                )
            item = value[key]
            is_tuple = isinstance(item, tuple)
            if is_tuple:
                if not checkers.is_string(item[0]):
                    raise errors.RequestError(
                        "First item in a file tuple must be a filename, "
                        "expressed as a string. Found %s, expressed as a "
                        "%s" % (item[0], item[0].__class__.__name__)
                    )
            if is_tuple and len(item) > 2:
                if not checkers.is_string(item[2]):
                    raise errors.RequestError(
                        "Third item in a file tuple must be a content-type, "
                        "expressed as a string. Found %s expressed as a "
                        "%s" % (item[2], item[2].__class__.__name__)
                    )
            if is_tuple and len(item) == 4:
                if not checkers.is_dict(item[3]):
                    raise errors.RequestError(
                        "Fourth item in a file tuple must be a dict with "
                        "custom headers. Found an object of type: "
                        "%s" % item[3].__class__.__name__
                    )

    return value


def _validate_cert(cert):
    """Validate that the cert parameter matches the structure expected by the
    requests library.

    :rtype: path-like object / :class:`tuple <python:tuple>` / :obj:`None <python:None>`
    """

    if value and checkers.is_file(value):
        return value
    elif value:
        value = validators.iterable(value,
                                    allow_empty = False,
                                    minimum_length = 2,
                                    maximum_length = 2)
        return (value[0], value[1])

    return None


class UrllibClient(HTTPClient):
    """class:`HTTPClient` for the :doc:`urllib <python:urllib>` and
    :doc:`urllib2 <python27:urllib2>` :term:`HTTP Libraries <HTTP Library>`.
    """

    name = "urllib.request"

    def __init__(self,
                 timeout = None,
                 allow_redirects = True,
                 length_limit = None,
                 random_user_agent = False,
                 **kwargs):
        """

        .. seealso::

          Parameters for :class:`HTTPClient`.

        :param timeout: Sets the maximum time to wait for an HTTP response
          before the requests library times out. Defaults to
          :obj:`None <python:None>`.
        :type timeout: :class:`float <python:float>` / :obj:`None <python:None>`

        :param allow_redirects: If ``True``, will automatically follow redirect
          responses. Defaults to ``True``.
        :type allow_redirects: :class:`bool <python:bool>`

        :param files: Files to upload using multipart mime-encoding.
          Defaults to :obj:`None <python:None>`.
        :type files: :class:`dict <python:dict>` of file-like objects with
          structure of ``{'name': object}`` where ``object`` may either be a
          file-like Python object, a 2-tuple ``('filename', fileobj)``, a
          3-tuple ``('filename', fileobj, 'content-type')``, or a 4-tuple
          ``('filename', fileobj, 'content-type', custom_headers)`` where
          ``'content-type'`` is a string indicating the file's content type,
          and ``custom_headers`` is a :class:`dict <python:dict>` containing
          additional headers to add for the file.

        :param CA_bundle: Path to a CA bundle to use for SSL transactions.
          Defaults to :obj:`None <python:None>`.
        :type CA_bundle: path-like object

        :param cert: Path to the SSL client certificate file (.pem file) or
          a (`cert`, `key`) pair. Defaults to :obj:`None <python:None>`.
        :type cert: path-like object / :class:`tuple <python:tuple>` with 2
          values / :obj:`None <python:None>`.

        :param kwargs: Additional keyword arguments that will be passed to the
          :doc:`urlfetch <urlfetch:index>` library when executing a request.

        :returns: An :class:`HTTPClient` instance designed to wrap the
          :doc:`urlfetch <urlfetch:index>` library.
        :rtype: :class:`UrlFetchClient` (inherits from :class:`HTTPClient`)

        """
        self._timeout = None
        self._allow_redirects = True
        self._files = None
        self._CA_bundle = None
        self._cert = None

        self._opener = None

        super(UrllibClient, self).__init__(**kwargs)

        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.files = files
        self.CA_bundle = CA_bundle
        self.cert = cert

        if self.has_proxy:
            proxy = urllib.request.ProxyHandler(self.proxy)
            self._opener = urllib.request.build_opener(proxy)

    @property
    def has_proxy(self):
        """Indicates whether a proxy server is configured for the client.

        :rtype: :class:`bool <python:bool>`
        """
        return self.proxy['http'] or self.proxy['https']

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
    def allow_redirects(self):
        """Determines whether to automatically follow redirects returned as a
        response.

        If ``True``, redirects are transparently and automatically followed,
        and the response contains the final destination’s payload.

        If ``False``, you see the HTTP response, including the `Location`
        header, and redirects are *not* automatically followed.

        :rtype: :class:`bool <python:bool>`
        """
        return self._allow_redirects

    @allow_redirects.setter
    def allow_redirects(self, value):
        self._allow_redirects = bool(value)

    @property
    def files(self):
        """Files to upload using multipart mime-encoding.

        :rtype: :class:`dict <python:dict>` of file-like objects with
          structure of ``{'name': object}`` where ``object`` may either be a
          file-like Python object, a 2-tuple ``('filename', fileobj)``, a
          3-tuple ``('filename', fileobj, 'content-type')``, or a 4-tuple
          ``('filename', fileobj, 'content-type', custom_headers)`` where
          ``'content-type'`` is a string indicating the file's content type,
          and ``custom_headers`` is a :class:`dict <python:dict>` containing
          additional headers to add for the file.

        """
        return self._files

    @files.setter
    def files(self, value):
        self._files = _validate_files(value)

    @property
    def CA_bundle(self):
        """The path to the CA bundle to use when making requests.

        :rtype: path-like object / :obj:`None <python:None>`
        """
        return self._CA_bundle

    @CA_bundle.setter
    def CA_bundle(self, value):
        self._CA_bundle = validators.path_exists(value, allow_empty = True)

    @property
    def cert(self):
        """Client certificate information to use when making requests.

        Either the path to a client certificate file (.pem file), a 2-tuple
        with (``cert``, ``key``), or :obj:`None <python:None>`.

        :rtype: path-like object / :class:`tuple <python:tuple>` /
          :obj:`None <python:None>`
        """
        return self._cert

    @cert.setter
    def cert(self, value):
        self._cert = _validate_cert(value)

    def _request(self,
                 method,
                 url,
                 parameters = None,
                 headers = None,
                 request_body = None,
                 **kwargs):
        timeout = kwargs.pop('timeout', self.deadline)
        allow_redirects = kwargs.pop('allow_redirects', self.allow_redirects)
        files = kwargs.pop('files', self.files)
        CA_bundle = kwargs.pop('CA_bundle', self.CA_bundle)
        verify = kwargs.pop('verify', self.verify_ssl_certs)
        cert = kwargs.pop('cert', self.cert)

        cookies = kwargs.pop('cookies', None)
        json_ = kwargs.pop('json', None)
        stream = kwargs.pop('stream', False)

        timeout = validators.integer(timeout,
                                     allow_empty = True,
                                     minimum = 0)
        allow_redirects = bool(allow_redirects)
        files = _validate_files(files)
        verify = checkers.is_on_filesystem(CA_bundle) or self.verify_ssl_certs
        cert = _validate_cert(cert)

        if json_ and not request_body:
            request_body = json_

        request = urllib.request.Request(url, request_body, headers)

        if method not in ("GET", "POST"):
            request.get_method = method

        request_kwargs = {}
        if timeout:
            request_kwargs['timeout'] = timeout
        if checkers.is_file(CA_bundle):
            request_kwargs['cafile'] = CA_bundle
        elif checkers.is_directory(CA_bundle):
            request_kwargs['capath'] = CA_bundle

        try:
            # use the custom proxy tied opener, if any.
            # otherwise, fall to the default urllib opener.
            if self._opener and request_kwargs:
                response = self._opener.open(request,
                                             **request_kwargs)
            elif self._opener:
                response = self._opener.open(request)
            elif request_kwargs:
                response = urllib.request.urlopen(request,
                                                  **request_kwargs)
            else:
                response = urllib.request.urlopen(request,
                                                  **request_kwargs)

            rbody = response.read()
            rcode = response.code
            response_headers = dict(response.info())
            if hasattr(response, 'close'):
                response.close()
        except urllib.error.HTTPError as error:
            rcode = error.code
            rbody = error.read()
            response_headers = dict(error.info())
            if hasattr(error, 'close'):
                error.close()
        except (urllib.error.URLError, ValueError) as error:
            raise errors.InvalidURLError(
                "The URL requested (%s) was empty or invalid." % url
            )
        except urllib.error.ContentTooShortError as error:
            raise errors.ResponseError(
                "The response was too large and was therefore truncated."
            )


        response = HTTPResponse(content = rbody,
                                status_code = rcode,
                                headers = response_headers)

        return response, response.status_code

    def close(self):
        """Closes an existing HTTP connection/session."""
        pass
