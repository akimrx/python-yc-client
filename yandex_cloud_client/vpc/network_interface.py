#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Instance, Metadata, SchedulingPolicy, Resources classes."""

import logging

from yandex_cloud_client.utils.helpers import universal_obj_hook
from yandex_cloud_client.base import YandexCloudObject
from yandex_cloud_client.vpc.address import Address

logger = logging.getLogger(__name__)


class NetworkInterface(YandexCloudObject):
    """This object represents a network interfaces of instance."""

    def __init__(self,
                 index=None,
                 mac_address=None,
                 subnet_id=None,
                 primary_v4_address=None,
                 primary_v6_address=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.index = index
        self.mac_address = mac_address
        self.subnet_id = subnet_id
        self.primary_v4_address = primary_v4_address
        self.primary_v6_address = primary_v6_address

        self.client = client
        self._id_attrs = (self.index, self.mac_address,)

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(NetworkInterface, cls).de_json(data, client)
        data['primary_v4_address'] = Address.de_json(universal_obj_hook(data.get('primary_v4_address')), client)
        data['primary_v6_address'] = Address.de_json(universal_obj_hook(data.get('primary_v6_address')), client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        interfaces = list()
        for interface in data:
            interfaces.append(cls.de_json(interface, client))

        return interfaces
