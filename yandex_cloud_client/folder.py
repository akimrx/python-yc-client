#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Folder class."""

from yandex_cloud_client.base import YandexCloudObject
from yandex_cloud_client.utils.helpers import string_to_datetime


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
        self.created_at = string_to_datetime(created_at) if created_at is not None else created_at
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

    def operations(self, *args, **kwargs):
        """Shortcut for client.folder_operations()."""
        return self.client.folder_operations(self.id, *args, **kwargs)

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


class FolderSpec(YandexCloudObject):
    """This object represents a specification for new folder."""

    def __init__(self,
                 cloud_id=None,
                 name=None,
                 description=None,
                 labels=None,
                 client=None,
                 **kwargs):

        self.cloudId = cloud_id
        self.name = name
        self.description = description
        self.labels = labels

        self.client = client

    @classmethod
    def prepare(cls, data: dict, client):
        """Deserializing and preparing for a request."""
        if not data:
            return None

        data = super(FolderSpec, cls).de_json(data, client)
        result = cls(client=client, **data).to_dict()

        # cleaning None-type keys
        cleaner = lambda x: dict((k, v) for (k, v) in x.items() if v is not None)

        return cleaner(result)
