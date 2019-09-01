# -*- coding: utf-8 -*-

"""
##############################################
universal_http_client.ext.PycurlClient
##############################################

Implements support for the :doc:`pycurl <requests:pycurl>` :term:`HTTP Library`.


"""
import email
import io
import warnings

try:
    import simplejson as json
except ImportError:
    import json

from validator_collection import validators, checkers

import six
from six.moves.urllib.parse import urlparse


from universal_http_client.HTTPClient import HTTPClient
from universal_http_client.HTTPResponse import HTTPResponse
from universal_http_client import errors
from universal_http_client.utilities import to_utf8

import pycurl

def _validate_files(files):
    """Validate that a ``files`` parameter matches the structure expected by the
    Pycurl library.

    :returns: A pycurl-compatible ``files`` parameter.
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


class PycurlClient(HTTPClient):
    """class:`HTTPClient` for the :doc:`pycurl <pycurl:index>` library.
    """

    name = "pycurl"

    def __init__(self,
                 timeout = 0,
                 connection_timeout = 300,
                 allow_redirects = True,
                 max_redirects = -1,
                 length_limit = None,
                 CA_bundle = None,
                 files = None,
                 **kwargs):
        """

        .. seealso::

          Parameters for :class:`HTTPClient`.

        :param timeout: Sets the maximum time in seconds to wait for an HTTP
          response before the library times out. Defaults to
          :obj:`None <python:None>`.
        :type timeout: :class:`int <python:int>` / :obj:`None <python:None>`

        :param connection_timeout: Sets the maximum time in seconds to wait for
          a connection to the HTTP server to be established before the library
          times out. Defaults to 300.
        :type connection_timeout: :class:`int <python:int>`

        :param allow_redirects: If ``True``, will automatically follow redirect
          responses. Defaults to ``True``.
        :type allow_redirects: :class:`bool <python:bool>`

        :param max_redirects: The maximum number of redirect responses to
          automatically follow. Defaults to ``-1`` (for an infinite number of
          redirects).
        :type max_redirects: :class:`int <python:int>`

        :param length_limit: The maximum number of bytes to receive. If a
          response exceeds the limit specified, will raise a
          :class:`ResponseError <universal_http_client.errors.ResponseError>`.
          If :obj:`None <python:None>`, no limit will be imposed. Defaults to
          :obj:`None <python:None>`.
        :type length_limit: :class:`int <python:int>`

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
        self._timeout = 0
        self._connection_timeout = 300
        self._allow_redirects = True
        self._max_redirects = -1
        self._length_limit = None
        self._CA_bundle = None
        self._files = None

        super(PycurlClient, self).__init__(**kwargs)

        self.timeout = timeout
        self.connection_timeout = connection_timeout
        self.allow_redirects = allow_redirects
        self.max_redirects = max_redirects
        self.length_limit = length_limit
        self.CA_bundle = CA_bundle
        self.files = files

        # Initialize this within the object so that we can reuse connections.
        self._curl = pycurl.Curl()

        # need to urlparse the proxy, since PyCurl
        # consumes the proxy url in small pieces
        for scheme in self._proxy:
            self._proxy[scheme] = urlparse(self._proxy[scheme])

    @property
    def timeout(self):
        """The maximum time to wait for an HTTP response before the HTTP library
        times out. Set to 0 for infinite time.

        :rtype: :class:`int <python:int>`
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = validators.integer(value,
                                           allow_empty = True,
                                           minimum = 0)

    @property
    def connection_timeout(self):
        """The maximum time to wait for a connection with the HTTP server
        before the HTTP library times out.

        :rtype: :class:`int <python:int>`
        """
        return self._connection_timeout

    @connection_timeout.setter
    def connection_timeout(self, value):
        self._connection_timeout = validators.integer(value,
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
    def max_redirects(self):
        """The maximum number of redirects to automatically follow.

        :rtype: :class:`int <python:int>`
        """
        if not self.allow_redirects:
            return 0

        return self._max_redirects

    @max_redirects.setter
    def max_redirects(self, value):
        if value is None:
            value = 0

        self._max_redirects = validators.integer(value,
                                                 allow_empty = False,
                                                 minimum = -1)

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
    def CA_bundle(self):
        """The path to the CA bundle to use when making requests.

        :rtype: path-like object / :obj:`None <python:None>`
        """
        return self._CA_bundle

    @CA_bundle.setter
    def CA_bundle(self, value):
        self._CA_bundle = validators.path_exists(value, allow_empty = True)

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

    def parse_headers(self, data):                                                        # pylint: disable=R0201
        """Parse headers into a :class:`dict <python:dict>`

        :param data: A string-like object with header data.
        :type data: :class:`bytes <python:bytes>` / :class:`str <python:str>`

        :returns: Dictionary of HTTP headers.
        :rtype: :class:`dict <python:dict>`
        """
        if "\r\n" not in data:
            return {}
        raw_headers = data.split("\r\n", 1)[1]

        headers = email.message_from_string(raw_headers)

        return dict((k.lower(), v) for k, v in six.iteritems(dict(headers)))

    def _request(self,
                 method,
                 url,
                 parameters = None,
                 headers = None,
                 request_body = None,
                 **kwargs):
        if isinstance(request_body, dict):
            request_body = json.dumps(request_body)

        timeout = kwargs.pop('timeout', self.timeout)
        connection_timeout = kwargs.pop('connection_timeout',
                                        self.connection_timeout)
        allow_redirects = bool(kwargs.pop('allow_redirects',
                                          self.allow_redirects))
        max_redirects = kwargs.pop('max_redirects', self.max_redirects)
        length_limit = kwargs.pop('length_limit', self.length_limit)
        verify_ssl_certs = bool(kwargs.pop('verify_ssl_certs',
                                           self.verify_ssl_certs))
        CA_bundle = kwargs.pop('CA_bundle', self.CA_bundle)
        files = kwargs.pop('files', self.files)

        if timeout:
            timeout = validators.integer(timeout,
                                         allow_empty = False,
                                         minimum = 0)

        if connection_timeout is not None:
            connection_timeout = validators.integer(connection_timeout,
                                                    allow_empty = False,
                                                    minimum = 0)
        else:
            connection_timeout = 0

        if max_redirects:
            max_redirects = validators.integer(max_redirects,
                                               allow_empty = True,
                                               minimum = -1)
        if length_limit:
            length_limit = validators.integer(length_limit, minimum = 0)

        if CA_bundle:
            CA_bundle = validators.path_exists(CA_bundle, allow_empty = True)

        if files:
            files = _validate_files(files)


        b = io.BytesIO()
        rheaders = io.BytesIO()

        # Pycurl's design is a little weird: although we set per-request
        # options on this object, it's also capable of maintaining established
        # connections. Here we call reset() between uses to make sure it's in a
        # pristine state, but notably reset() doesn't reset connections, so we
        # still get to take advantage of those by virtue of re-using the same
        # object.
        self._curl.reset()

        proxy = self._get_proxy(url)
        if proxy:
            if proxy.hostname:
                self._curl.setopt(pycurl.PROXY, proxy.hostname)
            if proxy.port:
                self._curl.setopt(pycurl.PROXYPORT, proxy.port)
            if proxy.username or proxy.password:
                self._curl.setopt(
                    pycurl.PROXYUSERPWD,
                    "%s:%s" % (proxy.username, proxy.password),
                )

        if method == "GET":
            self._curl.setopt(pycurl.HTTPGET, 1)
        elif method == 'HEAD':
            self._curl.setopt(pycurl.NOBODY, 1)
        elif method == "POST":
            self._curl.setopt(pycurl.POST, 1)
            self._curl.setopt(pycurl.POSTFIELDS, request_body)
        elif method == 'PUT':
            self._curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
            self._curl.setopt(pycurl.POSTFIELDS, request_body)
        elif method == 'PATCH':
            self._curl.setopt(pycurl.CUSTOMREQUEST, 'PATCH')
            self._curl.setopt(pycurl.POSTFIELDS, request_body)
        else:
            self._curl.setopt(pycurl.CUSTOMREQUEST, method.upper())

        # pycurl doesn't like unicode URLs
        if parameters:
            parameter_string = base_urllib.urlencode(parameters)

            url += '?' + parameter_string

        url = to_utf8(url)
        self._curl.setopt(pycurl.URL, url)

        file_list = []
        if files and method == 'POST':
            for key in files:
                if checkers.is_file(files[key]):
                    file_item = (key, (pycurl.FORM_FILE, files[key],))
                elif not isinstance(files[key], tuple):
                    file_item = (key, (pycurl.FORM_BUFFER,
                                       key,
                                       pycurl.FORM_BUFFERPTR,
                                       files[key]))
                elif isinstance(files[key], tuple):
                    item = files[key]
                    if len(item) == 2:
                        file_item = (key, (pycurl.FORM_BUFFER,
                                           item[0],
                                           pycurl.FORM_BUFFERPTR,
                                           item[1]))
                    elif len(item) >= 3:
                        file_item = (key, (pycurl.FORM_BUFFER,
                                           item[0],
                                           pycurl.FORM_BUFFERPTR,
                                           item[1],
                                           pycurl.FORM_CONTENT_TYPE,
                                           item[2]))
                file_list.append(file_item)
                self._curl.setopt(pycurl.HTTPPOST, [*file_list])
        elif files and method == 'PUT':
            self._curl.setopt(pycurl.UPLOAD, 1)
            for key in files:
                if checkers.is_file(files[key]):
                    with open(files[key], mode = 'rb') as file_:
                        file_contents = file_.read()
                    self._curl.setopt(pycurl.READDATA, file_contents)
                elif not isinstance(files[key], tuple):
                    self._curl.setopt(pycurl.READDATA, files[key])
                elif isinstance(files[key], tuple):
                    item = files[key]
                    self._curl.setopt(pycurl.READDATA, item[1])

        if allow_redirects and max_redirects:
            self._curl.setopt(pycurl.FOLLOWLOCATION, 1)
            self._curl.setopt(pycurl.MAXREDIRS, max_redirects)

        if length_limit:
            if length_limit >= 2147483648:
                self._curl.setopt(pycurl.MAXFILESIZE_LARGE, length_limit)
            else:
                self._curl.setopt(pycurl.MAXFILESIZE, length_limit)


        self._curl.setopt(pycurl.WRITEFUNCTION, b.write)
        self._curl.setopt(pycurl.HEADERFUNCTION, rheaders.write)
        self._curl.setopt(pycurl.NOSIGNAL, 1)
        self._curl.setopt(pycurl.TIMEOUT, timeout)
        self._curl.setopt(pycurl.CONNECTTIMEOUT, connection_timeout)

        if headers:
            self._curl.setopt(
                pycurl.HTTPHEADER,
                ["%s: %s" % (k, v) for k, v in six.iteritems(dict(headers))],
            )

        if self.verify_ssl_certs and self.CA_bundle:
            self._curl.setopt(pycurl.CAINFO, self.CA_bundle)
        else:
            self._curl.setopt(pycurl.SSL_VERIFYHOST, False)

        try:
            self._curl.perform()
        except pycurl.error as error:
            self._handle_request_error(error,
                                       max_redirects = max_redirects,
                                       length_limit = length_limit)

        rbody = b.getvalue().decode("utf-8")
        rcode = self._curl.getinfo(pycurl.RESPONSE_CODE)
        headers = self.parse_headers(rheaders.getvalue().decode("utf-8"))

        response = HTTPResponse(content = rbody,
                                status_code = rcode,
                                headers = headers)

        return response, response.status_code

    @classmethod
    def _handle_request_error(cls,
                              error,
                              max_redirects = -1,
                              length_limit = None):
        if error.args[0] == pycurl.E_OPERATION_TIMEOUTED:
            raise HTTPTimeoutError('Unable to connect to the HTTP Server (timeout). '
                                   'Please check your internet connection and try again. ')
        elif error.args[0] == [pycurl.E_COULDNT_CONNECT,
                               pycurl.E_COULDNT_RESOLVE_HOST]:
            raise HTTPConnectionError("Could not connect to the HTTP Server. Please check "
                                      "your internet connection and try again.")
        elif error.args[0] in [pycurl.E_SSL_CACERT,
                               pycurl.E_SSL_PEER_CERTIFICATE]:
            raise SSLError("Could not verify SSL certificates.  Please make "
                           "sure that your network is not intercepting certificates.")
        elif error.args[0] == pycurl.E_FILESIZE_EXCEEDED:
            raise errors.ResponseError(
                'The response would have exceeded the content limit '
                '(%d bytes)' % length_limit
            )
        elif error.args[0] == pycurl.E_TOO_MANY_REDIRECTS:
            raise errors.ResponseError(
                "The redirect limit configured in the request or set by default "
                "(%s) was reached before a response was returned." % max_redirects
            )
        else:
            raise HTTPConnectionError(
                "Unexpected error communicating with the HTTP Server. If this "
                "problem persists, let us know at software@insightindustry.com."
            )

    def _get_proxy(self, url):
        proxy = self.proxy
        scheme = url.split(":")[0] if url else None
        if scheme:
            if scheme in proxy:
                return proxy[scheme]

            scheme = scheme[0:-1]

            if scheme in proxy:
                return proxy[scheme]

        return None

    def close(self):
        """Closes an existing HTTP connection/session."""
        pass
