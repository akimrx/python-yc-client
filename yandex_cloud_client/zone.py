#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Zone class."""

from yandex_cloud_client.base import YandexCloudObject


class Zone(YandexCloudObject):
    """This object represents the availability zone."""

    def __init__(self,
                 id=None,
                 region_id=None,
                 status=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.id = id
        self.region_id = region_id
        self.status = status

        self.client = client
        self._id_attrs = (self.id, self.region_id, self.status)


    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Zone, cls).de_json(data, client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        zones = list()
        for zone in data:
            zones.append(cls.de_json(zone, client))

        return zones
