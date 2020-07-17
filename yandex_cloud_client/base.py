#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains YandexCloudObject parent class."""

import json
import logging

from abc import ABCMeta

logger = logging.getLogger(__name__)


class YandexCloudObject(object):
    """Base class for Yandex.Cloud objects."""

    __metaclass__ = ABCMeta
    _id_attrs = ()

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self)

    def __getitem__(self, item):
        return self.__dict__[item]

    @staticmethod
    def handle_unknown_kwargs(obj, **kwargs):
        """Logging unparsed fields from Yandex.Cloud API."""
        if kwargs:
            logger.debug(f'Unparsed fields received from API')
            logger.debug(f'Type: {type(obj)}; kwargs: {kwargs}')

    @classmethod
    def de_json(cls, data: dict, client):
        """Deserialize object."""
        if not data:
            return None

        data = data.copy()
        return data

    def to_json(self):
        """Serialize object to json."""
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        """Recursive serialize object."""
        def parse(val):
            if hasattr(val, 'to_dict'):
                return val.to_dict()
            elif isinstance(val, list):
                return [parse(it) for it in val]
            elif isinstance(val, dict):
                return {key: parse(value) for key, value in val.items()}
            else:
                return val

        data = self.__dict__.copy()
        data.pop('client', None)
        data.pop('_id_attrs', None)

        return parse(data)

    def to_clean_dict(self) -> dict:
        """Delete None-type key: value pairs."""

        data = self.to_dict().copy()
        cleaner = lambda x: dict((k, v) for (k, v) in x.items() if v is not None)
        return cleaner(data)

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self._id_attrs == other._id_attrs
        return super(YandexCloudObject, self).__eq__(other)

    def __hash__(self) -> int:
        if self._id_attrs:
            return hash((self.__class__, self._id_attrs))
        return super(YandexCloudObject, self).__hash__()
