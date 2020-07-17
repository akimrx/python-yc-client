#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Address, OneToOneNat and PrimaryV4,6Address classes."""
import logging

from yandex_cloud_client.base import YandexCloudObject
from yandex_cloud_client.utils.helpers import universal_obj_hook

logger = logging.getLogger(__name__)


class OneToOneNat(YandexCloudObject):
    """This object represents a one-to-one NAT address."""

    def __init__(self,
                 address=None,
                 ip_version=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.address = address
        self.ip_version = ip_version

        self.client = client
        self._id_attrs = (self.address, self.ip_version)

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(OneToOneNat, cls).de_json(data, client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        nats = list()
        for nat in data:
            nats.append(cls.de_json(nat, client))

        return nats


class Address(YandexCloudObject):
    """This object represents a base network address."""

    def __init__(self,
                 address=None,
                 one_to_one_nat=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.address = address
        self.one_to_one_nat = one_to_one_nat

        self.client = client
        self._id_attrs = (self.address,)

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Address, cls).de_json(data, client)
        data['one_to_one_nat'] = OneToOneNat.de_json(universal_obj_hook(data.get('one_to_one_nat')), client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        addresses = list()
        for address in data:
            addresses.append(cls.de_json(address, client))

        return addresses
