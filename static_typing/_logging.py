"""Default logging mechanism for static_typing module."""

import logging
import os

logging.basicConfig(
    level=getattr(logging, os.environ.get('LOGGING_LEVEL', 'warning').upper(), logging.WARNING))
