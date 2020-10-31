#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Operation and OperationWait classes."""

import time
import asyncio
import logging

from yandex_cloud_client.base import YandexCloudObject
from yandex_cloud_client.error import OperationDeadlineExceeded
from yandex_cloud_client.utils.helpers import string_to_datetime, universal_obj_hook
from yandex_cloud_client.utils.request import RpcError

logger = logging.getLogger(__name__)


class Operation(YandexCloudObject):
    """This object represents an operation."""

    def __init__(self,
                 id=None,
                 created_at=None,
                 created_by=None,
                 modified_at=None,
                 done=None,
                 response=None,
                 error=None,
                 metadata=None,
                 description=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        # Required
        self.id = id

        # Optional
        self.created_at = string_to_datetime(created_at) if created_at is not None else created_at
        self.created_by = created_by
        self.modified_at = string_to_datetime(modified_at) if modified_at is not None else modified_at
        self.done = bool(done)
        self.response = response
        self.error = error
        self.metadata = metadata
        self.description = description

        self.client = client
        self._id_attrs = (self.id,)

    @property
    def failed(self):
        if self.error is not None:
            return True
        return False

    @property
    def completed(self):
        if self.done:
            return True
        return False

    def cancel(self, *args, **kwargs):
        """Shortcut for client.cancel_operation()."""
        return self.client.cancel_operation(self.id, *args, **kwargs)

    def update_status(self, *args, **kwargs):
        """Shortcut for client.operation()."""
        return self.client.operation(self.id, *args, **kwargs)

    @classmethod
    def de_json(cls, data, client):
        if not data:
            return None

        data = super(Operation, cls).de_json(data, client)
        data['metadata'] = OperationMetadata.de_json(universal_obj_hook(data.get('metadata')), client)
        data['error'] = OperationError.de_json(universal_obj_hook(data.get('error')), client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data, client):
        if not data:
            return []

        operations = list()
        for operation in data:
            operations.append(cls.de_json(operation, client))

        return operations


class OperationMetadata(YandexCloudObject):
    """This object represents an operation metadata."""

    def __init__(self,
                 instance_id=None,
                 disk_id=None,
                 snapshot_id=None,
                 image_id=None,
                 subnet_id=None,
                 network_id=None,
                 certificate_id=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.instance_id = instance_id
        self.disk_id = disk_id
        self.snapshot_id = snapshot_id
        self.image_id = image_id
        self.subnet_id = subnet_id
        self.network_id = network_id
        self.certificate_id = certificate_id

        self.client = client

    @classmethod
    def de_json(cls, data, client):
        if not data:
            return None

        data = super(OperationMetadata, cls).de_json(data, client)
        return cls(client=client, **data)


class OperationError(YandexCloudObject):
    """This object represents an operation metadata."""

    def __init__(self,
                 code=None,
                 message=None,
                 details=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.code = RpcError(int(code)) if code is not None else code
        self.message = message
        self.details = details

        self.client = client

    @classmethod
    def de_json(cls, data, client):
        if not data:
            return None

        data = super(OperationError, cls).de_json(data, client)
        return cls(client=client, **data)



class OperationWait:
    """This class represents an operation waiter."""

    def __init__(self, operation: Operation, delay=2, timeout=600,
                 client=None, **kwargs):

        self._operation = operation
        self._delay = int(delay)
        self._deadline = time.time() + int(timeout) if timeout is not None else None

        self.client = client

    @property
    def operation(self):
        return self._operation

    @property
    def completed(self):
        """Sync operation waiter."""
        while not self._wait_operation():
            logger.debug('Sleeping.. sync awaiting operation status..')
            time.sleep(self._delay)
        return self._wait_operation()

    async def await_complete_async(self):
        """Async operation waiter."""
        while not self._wait_operation():
            logger.debug('Async awaiting operation status..')
            await asyncio.sleep(self._delay)
        return self._wait_operation()

    def _wait_operation(self):
        self._operation = self._operation.update_status()

        if self._operation.failed:
            logger.debug('Operation failed!')
            raise RuntimeError(self._operation.error)

        elif self._operation.completed:
            logger.debug('Operation done!')
            return self._operation

        elif time.time() >= self._deadline:
            logger.debug('Deadline exceeded!')
            raise OperationDeadlineExceeded(self._operation.id,
                self._operation.description)
