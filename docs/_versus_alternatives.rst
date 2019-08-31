Since making and supporting HTTP requests is such a common need, there are obviously
a variety of alternative ways to support HTTP requests in your Python libraries.
Obviously, I'm biased in favor of the **Universal HTTP Client**. But
it might be helpful to compare the **Universal HTTP Client** to some
commonly-used alternatives:

.. tabs::

  .. tab:: Rolling Your Own

    Adding your own custom HTTP library wrapper Python library is a very viable
    strategy. It's what I did for years, until I got tired of repeating the same
    patterns over and over again, and decided to build the **Universal HTTP Client**
    instead.

    But of course, implementing an extensible HTTP library wrapper takes a bit
    of effort, especially if you want to support the various edge cases that
    your library's users might encounter "in the wild".

    .. tip::

      **When to use it?**

      In practice, I find that rolling my own solution is great when it's a simple
      library where I only need to support a limited number of deployment environments.
      It's a "quick-and-dirty" solution, where I'm trading rapid implementation
      (yay!) for less flexibility/functionality (boo!).

      Considering how easy the **Universal HTTP Client** is to configure / apply,
      however, I find that I never really roll my own library wrapper anymore.

  .. tab:: Hard Dependency

    The most common situation, and one which unfortunately most Python libraries
    assume, is that you will always rely on a single HTTP library dependency.
    Whether that dependency is :doc:`requests <requests:index>`,
    :doc:`urlfetch <urlfetch:index>`, or the standard library, the most common
    approach I've seen is to always enforce a hard-and-fast / one-and-done
    dependency on a single HTTP library.

    Unfortunately, from a library development standpoint this is inherently
    limiting. When you build a hard dependency on a single HTTP library, you run
    the risk of missing practical requirements that your users may need (e.g.
    proxy support, SSL certificate support, etc.). Furthermore, you are
    inherently constraining the environments where your users may deploy their
    applications. For example, the Google Cloud Platform only supports the
    :doc:`urlfetch <urlfetch:index>` HTTP library.

    The biggest practical difference between implementing a hard dependency on
    an underlying HTTP library as opposed to using the **Universal HTTP Client**
    is "what you get" when doing the work. You'll need to do comparable
    implementation work to implement the **Universal HTTP Client**, but you get
    automatic support for five or more HTTP libraries with graceful fall-through
    based on the libraries available at runtime.

    .. tip::

      **When to use it?**

      These days I would only use the hard dependency pattern when I will always
      have absolute control over the development environment, which means that
      I will always be able to use whichever HTTP library I choose to be
      dependent on.

      Since the level of effort is the same to implement a hard dependency and
      the **Universal HTTP Client**, I find that I would always choose to go
      with the **Universal HTTP Client**.
