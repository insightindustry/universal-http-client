# -*- coding: utf-8 -*-

"""
#########################################
universal_http_client.utilities
#########################################

Implements utility functions and constants used by the **Universal HTTP Client**.

"""
import os
import time

from validator_collection import validators, checkers


HTTP_METHODS = ['GET',
                'HEAD',
                'OPTIONS',
                'POST',
                'PUT',
                'PATCH',
                'DELETE']


def _now_ms():
    """Returns the current time expressed in milliseconds.

    :rtype: :class:`int <python:int>`
    """
    return int(round(time.time() * 1000))


def to_utf8(value):
    """Return a UTF-8 encoded version of ``value`` if ``value`` is a string.

    :returns: ``value`` if ``value`` is not a string or UTF-8 encoded
      :class:`str <python:str>`
    """
    if is_py2 and checkers.is_string(value, coerce_value = True):
        value = validators.string(value, coerce_value = True)
        return value.encode("utf-8")

    return value
