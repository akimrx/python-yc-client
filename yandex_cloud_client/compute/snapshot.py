#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Snapshot class."""

from datetime import datetime

from yandex_cloud_client.constants import SECONDS_IN_DAY
from yandex_cloud_client.utils.helpers import string_to_datetime, human_readable_size
from yandex_cloud_client.base import YandexCloudObject


class Snapshot(YandexCloudObject):
    """This object represents a snapshot of the disk.

    Attributes:
      :id: str
      :folder_id: str
      :created_at: datetime
      :name: str
      :description: str
      :labels: list
      :storage_size: int
      :disk_size: int
      :product_ids: list
      :status: str
      :source_disk_id: str
      :client: object

    """

    def __init__(self,
                 id=None,
                 folder_id=None,
                 created_at=None,
                 name=None,
                 description=None,
                 labels=None,
                 storage_size=None,
                 disk_size=None,
                 product_ids=None,
                 status=None,
                 source_disk_id=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        # Required
        self.id = id

        # Optional
        self.folder_id = folder_id
        self.created_at = string_to_datetime(created_at) if created_at is not None else created_at
        self.name = name
        self.description = description
        self.labels = labels
        self.storage_size = int(storage_size) if storage_size is not None else storage_size
        self.disk_size = int(disk_size) if disk_size is not None else disk_size
        self.product_ids = product_ids
        self.status = status
        self.source_disk_id = source_disk_id

        self.client = client
        self._id_attrs = (self.id,)

    @property
    def age(self):
        """Snapshot age in days."""
        today = datetime.utcnow()
        if isinstance(self.created_at, datetime):
            _age = int((today - self.created_at).total_seconds()) // SECONDS_IN_DAY
            return _age
        return

    @property
    def human_readable_storage_size(self):
        """Converting bytes to human-readable size."""
        if self.storage_size is not None:
            return human_readable_size(self.storage_size)
        return self.storage_size

    @property
    def human_readable_disk_size(self):
        """Converting bytes to human-readable size."""
        if self.disk_size is not None:
            return human_readable_size(self.disk_size)
        return self.disk_size

    def delete(self, await_complete=True, run_async_await=False, *args, **kwargs):
        """Shortcut for client.delete_snapshot()."""
        return self.client.delete_snapshot(self.folder_id, self.id, await_complete=await_complete,
            run_async_await=run_async_await, *args, **kwargs)

    def update(self, *args, **kwargs):
        """Shortcut for client.update_snapshot()."""
        pass

    def operations(self, page_size=1000, *args, **kwargs):
        """Shortcut for snapshot_operations()."""
        return self.client.snapshot_operations(self.id, page_size=page_size, *args, **kwargs)

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Snapshot, cls).de_json(data, client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        snapshots = list()
        for snapshot in data:
            snapshots.append(cls.de_json(snapshot, client))

        return snapshots



class SnapshotSpec(YandexCloudObject):
    """This object represents a new snapshot."""

    def __init__(self,
                 folder_id=None,
                 disk_id=None,
                 name=None,
                 description=None,
                 labels=None,
                 client=None,
                 **kwargs):

        self.folderId = folder_id
        self.diskId = disk_id
        self.name = name
        self.description = description
        self.labels = labels

        self.client = client

    @classmethod
    def prepare(cls, data: dict, client):
        if not data:
            return None

        data = super(SnapshotSpec, cls).de_json(data, client)
        return cls(client=client, **data).to_clean_dict()
