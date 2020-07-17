#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Cloud class."""

from yandex_cloud_client.base import YandexCloudObject


class Folder(YandexCloudObject):
    """This object represents a Folder."""

    def __init__(self,
                 id=None,
                 cloud_id=None,
                 created_at=None,
                 name=None,
                 description=None,
                 labels=None,
                 status=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.id = id
        self.cloud_id = cloud_id
        self.created_at = created_at
        self.name = name
        self.description = description
        self.labels = labels
        self.status = status

        self.client = client
        self._id_attrs = (self.id, self.cloud_id)

    def update(self):
        pass

    def delete(self):
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

        data = super(Folder, cls).de_json(data, client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        folders = list()
        for folder in data:
            folders.append(cls.de_json(folder, client))

        return folders
