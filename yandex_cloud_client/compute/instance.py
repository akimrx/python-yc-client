#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Instance, Metadata, SchedulingPolicy, Resources classes."""

import logging

from yandex_cloud_client.utils.helpers import universal_obj_hook, human_readable_size, string_to_datetime
from yandex_cloud_client.base import YandexCloudObject
from yandex_cloud_client.compute.disk import AttachedDisk, DiskSpec
from yandex_cloud_client.vpc.network_interface import NetworkInterface
from yandex_cloud_client.error import TooManyArguments

from yandex_cloud_client.constants import (MAX_INSTANCE_MEMORY, MIN_SHARED_INSTANCE_MEMORY, 
                                           INSTANCE_CORES, INSTANCE_CORE_FRACTIONS, IP_VERSIONS,
                                           INSTANCE_PLATFORMS, AZ)

logger = logging.getLogger(__name__)


STATES = (
    'PROVISIONING',
    'RUNNING',
    'STOPPING',
    'STOPPED',
    'STARTING',
    'RESTARTING',
    'UPDATING',
    'ERROR',
    'CRASHED',
    'DELETING',
)


class Instance(YandexCloudObject):
    """This object represents a instance.

    Attributes:
      :id: str
      :folder_id: str
      :created_at: datetime
      :name: str
      :description: str
      :labels: dict
      :zone_id: str
      :platform_id: str
      :resources: object
      :status: str
      :metadata: object
      :boot_disk: object
      :secondary_disk: list of obj
      :network_interfaces: list of obj
      :fqdn: str
      :scheduling_policy: object
      :service_account_id: str
      :network_settings: object
      :client: object

    """

    def __init__(self,
                 id=None,
                 folder_id=None,
                 created_at=None,
                 name=None,
                 description=None,
                 labels=None,
                 zone_id=None,
                 platform_id=None,
                 resources=None,
                 status=None,
                 metadata=None,
                 boot_disk=None,
                 secondary_disks=None,
                 network_interfaces=None,
                 fqdn=None,
                 scheduling_policy=None,
                 service_account_id=None,
                 network_settings=None,
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
        self.zone_id = zone_id
        self.platform_id = platform_id
        self.resources = resources
        self.status = status
        self.metadata = metadata
        self.boot_disk = boot_disk
        self.secondary_disks = secondary_disks
        self.network_interfaces = network_interfaces
        self.fqdn = fqdn
        self.scheduling_policy = scheduling_policy
        self.service_account_id = service_account_id
        self.network_settings = network_settings

        self.client = client
        self._id_attrs = (self.id,)

    @property
    def running(self):
        if self.status == 'RUNNING':
            return True
        return False

    @property
    def stopped(self):
        if self.status == 'STOPPED':
            return True
        return False

    @property
    def crashed(self):
        if self.status == 'CRASHED':
            return True
        return False

    @property
    def error(self):
        if self.status == 'ERROR':
            return True
        return False

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Instance, cls).de_json(data, client)
        data['boot_disk'].update({'attached_to': data.get('id', None)})
        data['boot_disk'].update({'folder_id': data.get('folder_id', None)})
        data['boot_disk'] = AttachedDisk.de_json(universal_obj_hook(data.get('boot_disk')), client)

        # add folder id and source instance id as attr to disks
        for disk in data.get('secondary_disks', []):
            if disk is not None:
                disk.update({'attached_to': data.get('id', None)})
                disk.update({'folder_id': data.get('folder_id', None)})

        data['secondary_disks'] = AttachedDisk.de_list(universal_obj_hook(data.get('secondary_disks')), client)
        data['network_interfaces'] = NetworkInterface.de_list(universal_obj_hook(data.get('network_interfaces')), client)
        data['resources'] = Resources.de_json(universal_obj_hook(data.get('resources')), client)
        data['metadata'] = Metadata.de_json(universal_obj_hook(data.get('metadata')), client)
        data['scheduling_policy'] = SchedulingPolicy.de_json(universal_obj_hook(data.get('scheduling_policy')), client)
        data['network_settings'] = NetworkSettings.de_json(universal_obj_hook(data.get('network_settings')), client)

        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        instances = list()
        for instance in data:
            instances.append(cls.de_json(instance, client))

        return instances

    def start(self, *args, **kwargs):
        """Shortcut for client.start_instance()."""
        return self.client.start_instance(self.id, *args, **kwargs)

    def restart(self, *args, **kwargs):
        """Shortcut for client.restart_instance()."""
        return self.client.restart_instance(self.id, *args, **kwargs)

    def stop(self, *args, **kwargs):
        """Shortcut for client.stop_instance()."""
        return self.client.stop_instance(self.id, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """Shortcut for client.delete_instance()."""
        return self.client.delete_instance(self.id, *args, **kwargs)

    def update(self, *args, **kwargs):
        """Shortcut for client.update_instance()."""
        pass

    def update_metadata(self, *args, **kwargs):
        """Shortcut for client.update_instance_metadata()."""
        pass

    def operations(self, *args, **kwargs):
        """Shortcut for client.instance_operations()."""
        return self.client.instance_operations(self.id, *args, **kwargs)

    def attach_new_disk(self, *args, **kwargs):
        """Create new disk and attach to the instance."""
        raise RuntimeError("Method not support yet")

    def attach_existent_disk(self, *args, **kwargs):
        """Shortcut for Client.instance_attach_existent_disk()."""
        return self.client.instance_attach_existent_disk(self.id, *args, **kwargs)

    def detach_disk(self, *args, **kwargs):
        """Shortcut for Client.instance_detach_disk()."""
        return self.client.instance_detach_disk(self.id, *args, **kwargs)

    def attached_disks(self, *args, **kwargs):
        """Shortcut for private method Client._convert_attached_disks()."""
        disks = [self.boot_disk.id] + [x.id for x in self.secondary_disks]
        return self.client._convert_attached_disks(disks, *args, **kwargs)

    def serial_port_output(self, *args, **kwargs):
        """Shortcut for client.instance_serial_port_output()."""
        return self.client.instance_serial_port_output(self.id, *args, **kwargs)


    # Aliases
    attachedDisks = attached_disks
    attachExistentDisk = attach_existent_disk
    attachNewDisk = attach_new_disk
    detachDisk = detach_disk
    updateMetadata = update_metadata
    serialPortOutput = serial_port_output


# Subsidiary classes for Instance object


class Metadata(YandexCloudObject):
    """This object represents a metadata of instance."""

    def __init__(self,
                 user_data=None,
                 serial_port_enable=None,
                 ssh_keys=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.user_data = user_data
        self.serial_port_enable = bool(int(serial_port_enable)) if serial_port_enable is not None else serial_port_enable
        self.ssh_keys = ssh_keys

        self.client = client
        self._id_attrs = (self.user_data, self.serial_port_enable, self.ssh_keys)

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Metadata, cls).de_json(data, client)
        return cls(client=client, **data)


class SchedulingPolicy(YandexCloudObject):
    """This object represents a sheduling policy options of instance."""

    def __init__(self,
                 preemptible=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.preemptible = bool(preemptible)
        self.client = client
        self._id_attrs = (self.preemptible,)

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(SchedulingPolicy, cls).de_json(data, client)
        return cls(client=client, **data)


class Resources(YandexCloudObject):
    """This object represents a resources of instance."""

    def __init__(self, memory=None, cores=None, core_fraction=None,
                 gpus=None, client=None, **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.memory = int(memory) if memory is not None else memory
        self.cores = int(cores) if cores is not None else cores
        self.core_fraction = int(core_fraction) if core_fraction is not None else core_fraction
        self.gpus = int(gpus) if gpus is not None else gpus

        self.client = client
        self._id_attrs = (self.memory, self.cores, self.core_fraction, self.gpus)

    @property
    def human_readable_memory(self):
        if self.memory is not None:
            return human_readable_size(self.memory)
        return self.memory

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Resources, cls).de_json(data, client)
        return cls(client=client, **data)


class NetworkSettings(YandexCloudObject):
    """This object represents a network settings of instance."""

    def __init__(self,
                 type=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.type = type
        self.client = client
        self._id_attrs = (self.type,)

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(NetworkSettings, cls).de_json(data, client)
        return cls(client=client, **data)


# Specifications for new instances

# FIXME: not completely done
class InstanceSpec(YandexCloudObject):
    """This object represents new instance spec."""

    def __init__(self,
                 folder_id=None,
                 name=None,
                 description=None,
                 labels=None,
                 zone_id=None,
                 platform_id=None,
                 resources_spec=None,
                 metadata=None,
                 boot_disk_spec=None,
                 secondary_disk_specs=None,
                 network_interface_specs=None,
                 hostname=None,
                 scheduling_policy=None,
                 service_account_id=None,
                 network_settings=None,
                 client=None,
                 **kwargs):

        self.folderId = folder_id
        self.name = name
        self.description = description
        self.labels = labels or {}
        self.zoneId = zone_id
        self.platformId = platform_id
        self.resourcesSpec = resources_spec
        self.metadata = metadata
        self.bootDiskSpec = boot_disk_spec
        self.secondaryDiskSpecs = secondary_disk_specs
        self.networkInterfaceSpecs = network_interface_specs
        self.hostname = hostname
        self.schedulingPolicy = scheduling_policy
        self.serviceAccountId = service_account_id
        self.networkSettings = network_settings

        self.client = client


    @classmethod
    def prepare(cls, data: dict, client):
        """Deserializing and preparing for a request."""
        if not data:
            return None

        data = super(InstanceSpec, cls).de_json(data, client)
        data['resourcesSpec'] = ResourcesSpec.de_json(data.get('resourcesSpec'), client)
        # data['bootDiskSpec'] = None
        # data['secondaryDiskSpecs'] = None
        # data['networkInterfaceSpecs'] = None
        # data['schedulingPolicy'] = None
        # data['networkSettings'] = None
        return cls(client=client, **data)


class ResourcesSpec(YandexCloudObject):
    """This object represents a resources specification for new instance."""

    def __init__(self,
                 memory=None,
                 cores=None,
                 core_fraction=None,
                 gpus=None,
                 client=None,
                 **kwargs):

        self.memory = int(memory) if memory is not None else memory
        self.cores = int(cores) if cores is not None else cores
        self.coreFraction = int(core_fraction) if core_fraction is not None else core_fraction
        self.gpus = int(gpus) if gpus is not None else gpus

        self.client = client

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(ResourcesSpec, cls).de_json(data, client)
        return cls(client=client, **data)
