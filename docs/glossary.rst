**********
Glossary
**********

.. glossary::

Default HTTP Client
  This is an instance of the :class:`HTTPClient` class which is automatically
  returned by the **Universal HTTP Client** library based upon the first
  :term:`HTTP Library` in your :term:`dependency chain` that is available in the code's
  runtime environment.

  In other words, if the code runs in an environment where the
  :doc:`requests <requests:index>` library is present, the Default HTTP Client
  will be an :class:`HTTPClient` instance that uses
  :doc:`requests <requests:index>` under the hood. If the code runs in an
  environment where the :doc:`urlfetch <urlfetch:index>` library is present, the
  Default HTTP Client will be an :class:`HTTPClient` instance that uses
  :doc:`urlfetch <urlfetch:index>` under the hood.

  .. seealso::

    * :data:`default_http_client <universal_http_client.default_http_client>`
    * :func:`get_default_http_client() <universal_http_client.HTTPClient.get_default_http_client>`

Dependency Chain
  An ordered list of :term:`HTTP libraries <HTTP Library>` that are tried in
  sequence by the **Universal HTTP Client** when creating the
  :term:`default HTTP client`.

  May either be defined in-code or using the ``HTTP_DEPENDENCY_CHAIN``
  environment variable.

  .. seealso::

    * :doc:`Configuring the Universal HTTP Client <configuring>` > :ref:`Dependency Chain Configuration <dependency_chain_configuration>`

HTTP Library
  A Python module or library that actually executes HTTP requests against a
  supplied URL and returns the response from the HTTP server to your Python code.
  Examples include :doc:`requests <requests:index>`,
  :doc:`urlfetch <urlfetch:index>`, or the :doc:`urllib <python:urllib>` /
  :doc:`urllib2 <python27:urllib2>` modules from the standard library.
