#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Cloud class."""

from yandex_cloud_client.base import YandexCloudObject


class Cloud(YandexCloudObject):
    """This object represents a Cloud."""

    def __init__(self,
                 id=None,
                 created_at=None,
                 name=None,
                 description=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.id = id
        self.created_at = created_at
        self.name = name
        self.description = description

        self.client = client
        self._id_attrs = (self.id,)

    def add_folder(self):
        pass

    def update(self):
        pass

    def operations(self):
        pass

    def folders(self):
        pass

    def show_access_bindings(self):
        pass

    def set_access_bindings(self):
        pass

    def update_access_bindings(self):
        pass

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Cloud, cls).de_json(data, client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        clouds = list()
        for cloud in data:
            clouds.append(cls.de_json(cloud, client))

        return clouds
