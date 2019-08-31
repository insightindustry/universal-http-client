.. SQLAthanor documentation master file, created by
   sphinx-quickstart on Fri Jun 15 11:08:09 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/universal-http-client-logo.png
  :alt: Universal HTTP Client - Flexible HTTP Library Support
  :align: right
  :width: 200
  :height: 100

|

####################################################
Universal HTTP Client
####################################################

**Flexible, Configurable, and Extensible HTTP Library Support**

.. sidebar:: Version Compatability

  The **Universal HTTP Client** is designed to be compatible with:

    * Python 2.7 and Python 3.4 or higher

.. include:: _unit_tests_code_coverage.rst

.. toctree::
 :hidden:
 :maxdepth: 3
 :caption: Contents:

 Home <self>
 Quickstart: Patterns and Best Practices <quickstart>
 Using the Universal HTTP Client <using>
 Extending the Universal HTTP Client <extending>
 API Reference <api>
 Error Reference <errors>
 Contributor Guide <contributing>
 Testing Reference <testing>
 Release History <history>
 Glossary <glossary>
 License <license>

 The **Universal HTTP Client** is designed to add flexible support for multiple
 HTTP libraries to your Python code using an internally consistent and naturally
 extensible API with additional robust features like configurable retry/back-off
 support. Built-in support for:

 * `urlfetch <https://pypi.org/project/urlfetch/>`_ (used on the Google Cloud Platform)
 * `requests <https://pypi.org/project/requests/2.7.0/>`_ (the Python community's favorite HTTP library)
 * `pycurl <http://pycurl.io>`_ (a Python wrapper to ``libcurl``)
 * `urllib3 <https://urllib3.readthedocs.io/en/latest/>`_
 * `urllib <https://docs.python.org/3/library/urllib.html>`_ / `urllib2 <https://docs.python.org/2/library/urllib2.html>`_ (using Python's standard library)

 with an extensible architecture that makes it easy to extend with support for
 additional HTTP libraries. Furthermore, the library  has been extensively tested on Python 2.7,
 3.4, 3.5, 3.6, and 3.7.

 .. note::

   The **Universal HTTP Client** is heavily inspired by the graceful cross-
   environment / cross-dependency support provided by the
   `Stripe API <https://stripe.com/docs/api>`_.

   Shout out and thanks to the Stripe development team!

.. contents::
 :depth: 3
 :backlinks: entry

-----------------

***************
Installation
***************

.. include:: _installation.rst

Dependencies
==============

.. include:: _dependencies.rst

-------------

************************************
Why the Universal HTTP Client?
************************************

If you've built Python code that makes HTTP calls, odds are that you've either
wrestled with the scaffolding of the standard library
(`urllib <https://docs.python.org/3/library/urllib.html>`_ or
`urllib2 <https://docs.python.org/2/library/urllib2.html>`_) or with one of the
many other HTTP libraries out there (e.g.
`requests <https://pypi.org/project/requests/2.7.0/>`_,
`urlfetch <https://pypi.org/project/urlfetch/>`_, etc.).

If you're building Python libraries that need to support HTTP calls, then you
run into the challenge of supporting multiple libraries (since some environments,
like the Google Cloud Platform) enforce a limited number of HTTP library options.

And if you want to support more complicated functionality, like proxy and SSL
certificate handling or retry/backoff strategies, things get even more complicated.

So the **Universal HTTP Client** is designed to simplify that by providing a
standardized, consistent, and tested API that wraps the major leading HTTP
libraries while being easy to extend. Thus, your code does not need to support
the branching semantics of different dependencies and you can simply let the
**Universal HTTP Client** handle all of that for you.

.. tip::

  The **Universal HTTP Client** is *NOT* a replacement for any other HTTP
  library. It is instead a wrapper around those HTTP libraries to provide for
  cross-dependency functionality.

Key Universal HTTP Client Features
=======================================

* **Easy to adopt**. Just write your code to leverage the simple ``.configure()``
  and ``.request()`` methods exposed by the ``HTTPClient`` class and its
  subclasses.
* Leverage a configurable dependency downgrade path, where the
  ``default_http_client`` automatically relies on the available / installed HTTP
  libraries.
* Leverage configurable retry / backoff strategies when executing your HTTP
  requests.

|

The **Universal HTTP Client** vs Alternatives
==================================================

.. include:: _versus_alternatives.rst

---------------

***********************************
Hello, World and Basic Usage
***********************************

1. Import the Default HTTP Client
========================================

The :term:`default HTTP client` is the instance of the **Universal HTTP Client**
that your code will use to execute HTTP requests. To use this instance, you need
to first import it from the library:

.. code-block:: python

  from universal_http_client import default_http_client

2. Configure Your HTTP Client (optional)
===========================================

.. seealso::

  * :doc:`Configuring the Universal HTTP Client <configuring>`

The default HTTP client comes preconfigured with a set of typical default
options, but if you want you can also adjust its configuration in a variety of
ways. You can configure:

* :ref:`dependency chain order <dependency_chain_configuration>`
* :ref:`proxy support <proxy_configuration>`
* :ref:`SSL certificate support <ssl_certificate_verification>`
* :ref:`retry strategies <retry_strategies>`
* :ref:`response error checking support <error_checking_configuration>`

3. Execute HTTP Requests
==================================

.. seealso::

  * :meth:`.request() <universal_http_client.HTTPClient.HTTPClient.request>`

.. code-block:: python

  method = 'GET'
  url = 'http://www.test.com'
  parameters = {
      'first': 123,
      'second': 456,
      'third': 'text-parameter'
  }
  headers = {
      'X-API-KEY': 'some-header-value-goes-here'
  }

  response, status_code = default_http_client.request(method,
                                                      url,
                                                      parameters = parameters,
                                                      headers = headers,
                                                      check_for_errors = True)

4. Check for Errors (optional)
==================================

.. seealso::

  * :func:`check_for_errors() <universal_http_client.errors.check_for_errors>`
  * :meth:`.request() <universal_http_client.HTTPClient.HTTPClient.request>`
  * :ref:`Response Error Checking Configuration <error_checking_configuration>`

While your application may want to handle HTTP request errors in its own special
way, you can also leverage the **Universal HTTP Client**'s own error-handling
capabilities to raise an appropriate exception based on the response received
from the URL you are requesting.

There are two ways to check the HTTP response for errors:

.. tabs::

  .. tab:: Synchronously

    This approach checks the response for errors as soon as it it is received
    and raises an appropriate exception based on the HTTP client's
    :ref:`error checking configuration <error_checking_configuration>`:

    .. code-block:: python

      response, status_code = default_http_client.request(method,
                                                          url,
                                                          parameters = parameters,
                                                          headers = headers,
                                                          check_for_errors = True)

  .. tab:: Asynchronously

    This approach checks the response for errors when you supply the response and
    status code to the
    :func:`check_for_errors() <universal_http_client.errors.check_for_errors>`
    function:

    .. code-block:: python

      response, status_code = default_http_client.request(method,
                                                          url,
                                                          parameters = parameters,
                                                          headers = headers,
                                                          check_for_errors = False)

      status_code, error_message = check_for_errors(response,
                                                    status_code,
                                                    raise_exception = True)


5. Work with the HTTP Response
==================================

.. seealso::

  * :class:`HTTPResponse <universal_http_client.HTTPResponse.HTTPResponse>`

Once you've received an HTTP response, you can work with it in a number of ways:

.. code-block:: python

  # EXAMPLE 1: Work with it as a raw string.
  raw_text = response.text

  # EXAMPLE 2: Work with it as raw bytes.
  raw_bytes = response.bytes

  # EXAMPLE 3: Deserialize JSON content to a dict.
  as_dict = response.to_dict()

And that's it!

--------------

*********************
Questions and Issues
*********************

You can ask questions and report issues on the project's
`Github Issues Page <https://github.com/insightindustry/universal-http-client/issues>`_

-----------------

*********************
Contributing
*********************

We welcome contributions and pull requests! For more information, please see the
:doc:`Contributor Guide <contributing>`

-------------------

*********************
Testing
*********************

We use `TravisCI <http://travisci.org>`_ for our build automation and
`ReadTheDocs <https://readthedocs.org>`_ for our documentation.

Detailed information about our test suite and how to run tests locally can be
found in our :doc:`Testing Reference <testing>`.

--------------------

**********************
License
**********************

The **Universal HTTP Client** is made available under an :doc:`MIT License <license>`.

----------------

********************
Indices and tables
********************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
