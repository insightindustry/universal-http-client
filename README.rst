####################################################
The Universal HTTP Client
####################################################

**Flexible HTTP Client with Graceful and Extensible Support for Key Python HTTP Libraries**

.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Branch
     - Unit Tests
   * - `latest <https://github.com/insightindustry/universal-http-client/tree/master>`_
     -
       .. image:: https://travis-ci.org/insightindustry/universal-http-client.svg?branch=master
         :target: https://travis-ci.org/insightindustry/universal-http-client
         :alt: Build Status (Travis CI)

       .. image:: https://codecov.io/gh/insightindustry/universal-http-client/branch/master/graph/badge.svg
         :target: https://codecov.io/gh/insightindustry/universal-http-client
         :alt: Code Coverage Status (Codecov)

       .. image:: https://readthedocs.org/projects/universal-http-client/badge/?version=latest
         :target: http://universal-http-client.readthedocs.io/en/latest/?badge=latest
         :alt: Documentation Status (ReadTheDocs)

   * - `v.0.1 <https://github.com/insightindustry/universal-http-client/tree/v.0.1.0>`_
     -
       .. image:: https://travis-ci.org/insightindustry/universal-http-client.svg?branch=v.0.1.0
         :target: https://travis-ci.org/insightindustry/universal-http-client
         :alt: Build Status (Travis CI)

       .. image:: https://codecov.io/gh/insightindustry/universal-http-client/branch/v.0.1.0/graph/badge.svg
         :target: https://codecov.io/gh/insightindustry/universal-http-client
         :alt: Code Coverage Status (Codecov)

       .. image:: https://readthedocs.org/projects/universal-http-client/badge/?version=v.0.1.0
         :target: http://universal-http-client.readthedocs.io/en/latest/?badge=v.0.1.0
         :alt: Documentation Status (ReadTheDocs)

   * - `develop <https://github.com/insightindustry/universal-http-client/tree/develop>`_
     -
       .. image:: https://travis-ci.org/insightindustry/universal-http-client.svg?branch=develop
         :target: https://travis-ci.org/insightindustry/universal-http-client
         :alt: Build Status (Travis CI)

       .. image:: https://codecov.io/gh/insightindustry/universal-http-client/branch/develop/graph/badge.svg
         :target: https://codecov.io/gh/insightindustry/universal-http-client
         :alt: Code Coverage Status (Codecov)

       .. image:: https://readthedocs.org/projects/universal-http-client/badge/?version=develop
         :target: http://universal-http-client.readthedocs.io/en/latest/?badge=develop
         :alt: Documentation Status (ReadTheDocs)

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

**COMPLETE DOCUMENTATION:** http://universal-http-client.readthedocs.org/en/latest/index.html

.. contents::
 :depth: 3
 :backlinks: entry

-----------------

***************
Installation
***************

To install the **Universal HTTP Client**, just execute:

.. code:: bash

 $ pip install universal-http-client


Dependencies
==============

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Python 3.x
     - Python 2.7
   * - | * `Validator-Collection v1.3 <https://github.com/insightindustry/validator-collection>`_ or higher
       | * `Backoff-Utils v.1.0 <https://github.com/insightindustry/validator-collection>`_ or higher
     - | * `Validator-Collection v1.3 <https://github.com/insightindustry/validator-collection>`_ or higher
       | * `Backoff-Utils v.1.0 <https://github.com/insightindustry/validator-collection>`_ or higher

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

**Universal HTTP Client** vs Alternatives
=============================================

For a comparison of the **Universal HTTP Client** to various alternative
HTTP library approaches, please see full documentation:
https://universal-http-client.readthedocs.io/en/latest/index.html#universal-http-client-vs-alternatives

------------------

***********************************
Complete Documentation
***********************************

The **Universal HTTP Client** is a robust library that integrates and extends
other complex libraries. We strongly recommend that you review our comprehensive
documentation at:

  https://universal-http-client.readthedocs.org/en/latest/index.html

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
`Contributor Guide <https://universal-http-client.readthedocs.io/en/latest/contributing.html>`_.

-------------------

*********************
Testing
*********************

We use `TravisCI <http://travisci.org>`_ for our build automation and
`ReadTheDocs <https://readthedocs.org>`_ for our documentation.

Detailed information about our test suite and how to run tests locally can be
found in our `Testing Reference <https://universal-http-client.readthedocs.io/en/latest/testing.html>`_.

--------------------

**********************
License
**********************

The **Universal HTTP Client** is made available under an
`MIT License <https://universal-http-client.readthedocs.io/en/latest/license.html>`_.
