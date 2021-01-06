#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Disk, AttachedDisk, AttachedDiskSpec and DiskSpec classes."""

import logging

from yandex_cloud_client.constants import MIN_DISK_SIZE, MAX_DISK_SIZE, DISK_MODES
from yandex_cloud_client.base import YandexCloudObject
from yandex_cloud_client.error import TooManyArguments
from yandex_cloud_client.utils.helpers import human_readable_size, string_to_datetime, disk_mode_converter

logger = logging.getLogger(__name__)


class Disk(YandexCloudObject):
    """This class representing a disk as an independent object.

    Different from AttachedDisk object.

    Attributes:
      :id: str
      :folder_id: str
      :created_at: datetime
      :name: str
      :description: str
      :labels: dict
      :type_id: str
      :zone_id: str
      :size: int
      :product_ids: list
      :status: str
      :instance_ids: list
      :source_image_id: str or None
      :source_snapshot_id: str or None
      :client: object

    """

    def __init__(self,
                 id=None,
                 folder_id=None,
                 created_at=None,
                 name=None,
                 description=None,
                 labels=None,
                 type_id=None,
                 zone_id=None,
                 size=None,
                 product_ids=None,
                 status=None,
                 instance_ids=None,
                 source_image_id=None,
                 source_snapshot_id=None,
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
        self.labels = labels or {}
        self.type_id = type_id
        self.zone_id = zone_id
        self.size = int(size) if size is not None else None
        self.product_ids = product_ids
        self.status = status
        self.instance_ids = instance_ids
        self.source_image_id = source_image_id
        self.source_snapshot_id = source_snapshot_id

        self.client = client
        self._id_attrs = (self.id,)

    @property
    def human_readable_size(self):
        """Converting bytes to human-readable size."""
        if self.size is not None:
            return human_readable_size(self.size)
        return self.size

    def delete(self, *args, **kwargs):
        """Shortcut client.delete_disk()."""
        return self.client.delete_disk(self.id, *args, **kwargs)

    def update(self, *args, **kwargs):
        """Shortcut for client.update_disk()."""
        pass

    def operations(self, *args, **kwargs):
        """Shortcut for client.disk_operations()."""
        return self.client.disk_operations(self.id, *args, **kwargs)

    def snapshots(self, *args, **kwargs):
        """Shortcut for client.snapshots_in_folder()."""
        result = list()
        snapshots = self.client.snapshots_in_folder(self.folder_id, *args, **kwargs)
        for snapshot in snapshots:
            if self.id == snapshot.source_disk_id:
                result.append(snapshot)
        return result

    def create_snapshot(self, *args, **kwargs):
        """Shortcut for client.create_snapshot()."""
        return self.client.create_snapshot(self.folder_id, self.id, *args, **kwargs)

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Disk, cls).de_json(data, client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        disks = list()
        for disk in data:
            disks.append(cls.de_json(disk, client))

        return disks


class AttachedDisk(YandexCloudObject):
    """This object represents a attached to the instance disk.

    Different from a Disk object.

    Attributes:
      :id: str
      :attached_to: str
      :mode: str
      :device_name: str
      :auto_delete: bool
      :folder_id: str
      :client: object

    """

    def __init__(self,
                 disk_id=None,
                 attached_to=None,
                 mode=None,
                 device_name=None,
                 auto_delete=None,
                 folder_id=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        # Required
        self.id = disk_id  # alias for disk_id
        self.disk_id = disk_id  # stay original attr

        # Optional
        self.folder_id = folder_id
        self.attached_to = attached_to
        self.mode = mode
        self.device_name = device_name
        self.auto_delete = auto_delete

        self.client = client
        self._id_attrs = (self.id,)

    def detach(self, await_complete=True, run_async_await=False, *args, **kwargs):
        """Shortcut for client.instance_detach_disk()."""
        return self.client.instance_detach_disk(self.attached_to, disk_id=self.id,
            await_complete=await_complete, run_async_await=run_async_await, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """Shortcut for client.delete_disk()."""
        return self.client.delete_disk(self.id, *args, **kwargs)

    def update(self, *args, **kwargs):
        """Shortcut for client.update_disk()."""
        pass

    def operations(self, page_size=1000, *args, **kwargs):
        """Shortcut for client.disk_operarions()."""
        return self.client.disk_operations(self.id, page_size=page_size, *args, **kwargs)

    def snapshots(self, query_filter=None, *args, **kwargs):
        """Shortcut for client.snapshots_in_folder()."""
        result = list()
        snapshots = self.client.snapshots_in_folder(self.folder_id, page_size=1000,
            query_filter=query_filter, *args, **kwargs)
        for snapshot in snapshots:
            if self.id == snapshot.source_disk_id:
                result.append(snapshot)
        return result

    def create_snapshot(self, name=None, description=None, labels=None, await_complete=True,
                        run_async_await=False, *args, **kwargs):
        """Shortcut for client.create_snapshot()."""
        return self.client.create_snapshot(self.folder_id, self.id, name=name, description=description, labels=labels,
            await_complete=await_complete, run_async_await=run_async_await, *args, **kwargs)

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(AttachedDisk, cls).de_json(data, client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        disks = list()
        for disk in data:
            disks.append(cls.de_json(disk, client))

        return disks


# Specifications for disks


class DiskSpec(YandexCloudObject):
    """This object represents new disk."""

    def __init__(self,
                 folder_id=None,
                 size=None,
                 zone_id=None,
                 name=None,
                 description=None,
                 labels=None,
                 type_id=None,
                 image_id=None,
                 snapshot_id=None,
                 client=None,
                 **kwargs):

        # Required
        self.folderId = folder_id
        self.size = int(size) if size is not None else size
        self.zoneId = zone_id

        # Optional
        self.name = name
        self.description = description
        self.labels = labels
        self.typeId = type_id
        self.imageId = image_id
        self.snapshotId = snapshot_id

        self.client = client
        self._validate()

    def _validate(self):
        if self.imageId and self.snapshotId:
            raise TooManyArguments('snapshot_id and image_id received, but you can use only one param')

        if self.size < MIN_DISK_SIZE or self.size > MAX_DISK_SIZE:
            raise ValueError(f'The disk size must be between {MIN_DISK_SIZE} and {MAX_DISK_SIZE} bytes')

    @classmethod
    def prepare(cls, data: dict, client):
        """Deserializing and preparing for a request."""
        if not data:
            return None

        data = super(DiskSpec, cls).de_json(data, client)
        result = cls(client=client, **data).to_dict()

        # cleaning None-type keys
        cleaner = lambda x: dict((k, v) for (k, v) in x.items() if v is not None)

        return cleaner(result)


class AttachedDiskSpec(YandexCloudObject):
    """This object represents existent or new disk,
    which will be immediately connected to the instance.

    """

    def __init__(self,
                 disk_id=None,
                 device_name=None,
                 mode=None,
                 auto_delete=None,
                 size=None,
                 name=None,
                 description=None,
                 labels=None,
                 type_id=None,
                 image_id=None,
                 snapshot_id=None,
                 client=None,
                 **kwargs):

        # Required for existent
        self.diskId = disk_id

        # Optional general
        self.deviceName = device_name
        self.mode = disk_mode_converter(mode) if mode is not None else mode
        self.autoDelete = auto_delete

        # Required for new
        self.size = int(size) if size is not None else size

        # Optional for new
        self.name = name
        self.description = description
        self.labels = labels
        self.typeId = type_id
        self.imageId = image_id
        self.snapshotId = snapshot_id

        self.client = client
        self._validate()

    def _validate(self):
        if self.imageId and self.snapshotId:
            raise TooManyArguments('snapshot_id and image_id received, but you can use only one param')

        if self.mode is not None and self.mode not in DISK_MODES:
            raise ValueError(f'Invalid disk mode: {self.mode}. Supported modes: {DISK_MODES}')

        if self.size is not None:
            if self.size < MIN_DISK_SIZE or self.size > MAX_DISK_SIZE:
                raise ValueError(f'The disk size must be between {MIN_DISK_SIZE} and {MAX_DISK_SIZE} bytes')

    @classmethod
    def prepare(cls, data: dict, client):
        """Deserializing and preparing for a request."""
        if not data:
            return None

        new = ('name', 'size', 'typeId', 'description', 'imageId', 'snapshotId')
        data = super(AttachedDiskSpec, cls).de_json(data, client)
        mdata = cls(client=client, **data).to_dict()

        # cleaning None-type keys
        cleaner = lambda x: dict((k, v) for (k, v) in x.items() if k not in new and v is not None)
        # separate and prepare diskSpec for new disk
        new_disk = lambda x: dict((k, v) for (k, v) in x.items() if k in new and v is not None)

        result = cleaner(mdata)
        result.update({'diskSpec': new_disk(mdata)})

        return result
