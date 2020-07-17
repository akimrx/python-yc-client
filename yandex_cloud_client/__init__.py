#!/usr/bin/env python3
"""A library that provides a Python interface to the Yandex.Cloud REST API."""

from .base import YandexCloudObject

from .client import YandexCloudClient, ComputeClient

from .cloud import Cloud
from .folder import Folder

from .compute.disk import Disk, DiskSpec, AttachedDisk, AttachedDiskSpec
from .compute.image import Image
from .compute.instance_group import InstanceGroup
from .compute.instance import Instance, InstanceSpec, ResourcesSpec
from .compute.placement_group import PlacementGroup
from .compute.snapshot import Snapshot

from .iam.service_account import ServiceAccountAuth

from .utils.decorators import retry, log
from .utils.helpers import generate_instance_yaml_example, instance_dict_example
from .utils.request import Request
from .utils.response import Response

from .vpc.address import Address, OneToOneNat
from .vpc.network_interface import NetworkInterface

from .operation import Operation, OperationWait
from .zone import Zone
from .version import __version__

__author__ = 'akimstrong@yandex.ru'

__all__ = [
    'YandexCloudObject', 'YandexCloudClient', 'ComputeClient', 'Disk', 'DiskSpec', 'AttachedDisk', 'AttachedDiskSpec',
    'Image', 'InstanceGroup', 'Instance', 'InstanceSpec', 'ResourcesSpec', 'Operation', 'OperationWait',
    'PlacementGroup', 'Snapshot', 'ServiceAccountAuth', 'retry', 'log', 'generate_instance_yaml_example',
    'instance_dict_example', 'Request', 'Response', 'Address', 'OneToOneNat', 'NetworkInterface',
    'Zone', 'Cloud', 'Folder', '__version__', '__author__'
]
