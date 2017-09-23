"""Unit tests for static_typing module."""

import logging

from static_typing import _logging

_LOG = logging.getLogger(__name__)
_LOG_LEVEL = logging.INFO

_LOG.setLevel(_LOG_LEVEL)
_LOG.log(_LOG_LEVEL, '%s logger level set to %s', __name__, logging.getLevelName(_LOG_LEVEL))
