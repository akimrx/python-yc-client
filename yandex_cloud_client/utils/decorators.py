#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains decorator functions."""

import time
import logging
from functools import wraps
from decorator import decorate

logger = logging.getLogger(__name__)


def retry(exceptions, tries=4, delay=5, backoff=2, logs=True):
    """Network errors decorator for retry requests."""
    def retry_decorator(func):
        @wraps(func)
        def func_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    msg = f'Retrying in {mdelay} seconds.. caused by NetworkError: {e}'
                    if logs:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return func(*args, **kwargs)
        return func_retry
    return retry_decorator


def log(func, *args, **kwargs):
    """Add debug messages to logger."""
    logger = logging.getLogger(func.__module__)

    def decorator(self, *args, **kwargs):
        logger.debug(f'Entering {func.__name__}')
        result = func(*args, **kwargs)
        logger.debug(result)
        logger.debug(f'Exiting {func.__name__}')
        return result

    return decorate(func, decorator)
