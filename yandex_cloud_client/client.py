#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains YandexCloudClient, ComputeClient classes"""

import json
import logging
import requests

from types import CoroutineType

from yandex_cloud_client.base import YandexCloudObject
from yandex_cloud_client.utils.request import Request
from yandex_cloud_client.utils.decorators import log
from yandex_cloud_client.utils.helpers import convert_yaml_to_dict
from yandex_cloud_client.utils.endpoints import (BASE_URL, IAM_URL, COMPUTE_URL, CERTIFICATE_URL,
                                                 OPERATION_URL, RESOURCE_MANAGER_URL, CERTIFICATE_DATA_URL)

from yandex_cloud_client.constants import BASE_HEADERS, DEFAULT_TIMEOUT
from yandex_cloud_client.error import (InvalidToken, YandexCloudError,
                                       TooManyArguments, BadRequest)

from yandex_cloud_client.iam.service_account import ServiceAccountAuth
from yandex_cloud_client.operation import Operation, OperationWait

from yandex_cloud_client.compute.disk import Disk, DiskSpec, AttachedDiskSpec
from yandex_cloud_client.compute.instance import Instance, InstanceSpec
from yandex_cloud_client.compute.snapshot import Snapshot, SnapshotSpec

from yandex_cloud_client.certificate import Certificate, CertificateRequestSpec, CertificateContent


logger = logging.getLogger(__name__)

# TODO (akimrx): add accessBindings for all clients
# TODO (akimrx): add pagintaion for list requests
# TODO (akimrx): add IAM methods to Base Client


class YandexCloudClient(YandexCloudObject):
    """Yandex.Cloud Client.
    Probably, this REST API Client will make your life with Yandex.Cloud a little easier.

    This parent Client contains authorization & general methods for services:
      - IAM
      - Operation
      - Resource Manager
      - Virtual Private Cloud

    Other services like a Compute, Managed Databases, etc — are inheritors of this client.
    For example, to work with the Compute service, use the `ComputeClient` class.
    It will already contain the methods of this client.

    Required Args:
      oauth_token: str
            or
      iam_token: str
            or
      service_account_key: dict

    Optional Args:
      request: Request
      base_url: str
      compute_url: str
      iam_url: str
      operation_url: str
      certificate_url: str
      certificate_data_url: str

    Methods:
      operation()                     -> return Operation object
      operation_cancel()              -> return Operation object

      """

    def __init__(self,
                 oauth_token: str = None,
                 iam_token: str = None,
                 service_account_key: dict = None,
                 request: object = None,
                 timeout: int = None,
                 base_url: str = None,
                 resource_manager_url: str = None,
                 compute_url: str = None,
                 certificate_url: str = None,
                 certificate_data_url: str = None,
                 iam_url: str = None,
                 operation_url: str = None):

        _cred_args = [x for x in (service_account_key, oauth_token, iam_token) if x is not None]
        if len(_cred_args) > 1:
            message = f'Too many credentials({len(_cred_args)}) received, ' + \
                      'but only one credential type can be specified'
            raise TooManyArguments(message)
        elif len(_cred_args) < 1:
            raise InvalidToken('IAM/OAuth token or service account key required!')

        if oauth_token:
            self.token = YandexCloudClient.get_iam_token(oauth_token)
        elif service_account_key:
            self.token = YandexCloudClient.get_token_for_sa(service_account_key)
        elif iam_token:
            self.token = iam_token
        else:
            raise InvalidToken('IAM/OAuth token or service account key required!')

        self.timeout = int(timeout) if timeout is not None else DEFAULT_TIMEOUT

        if request:
            self._request = request
            self._request.set_and_return_client(self)
        else:
            self._request = Request(self, timeout=self.timeout)

        self.base_url = base_url or BASE_URL
        self.iam_url = iam_url or IAM_URL
        self.resource_manager_url = resource_manager_url or RESOURCE_MANAGER_URL
        self.compute_url = compute_url or COMPUTE_URL
        self.certificate_url = certificate_url or CERTIFICATE_URL
        self.certificate_data_url = certificate_data_url or CERTIFICATE_DATA_URL
        self.operation_url = operation_url or OPERATION_URL

    @staticmethod
    def get_iam_token(oauth_token, raw=False) -> [str, dict]:
        url = f'{IAM_URL}/iam/v1/tokens'
        data = {'yandexPassportOauthToken': oauth_token}

        result = requests.post(url, json=data, headers=BASE_HEADERS)
        try:
            response = result.json()
        except json.decoder.JSONDecodeError:
            raise BadRequest(result.text)

        if not result.ok:
            raise BadRequest(result.text)

        if raw:
            return response
        return response.get('iamToken')

    @staticmethod
    def get_token_for_sa(sa_credentials: dict, raw=False) -> [str, dict]:
        url = f'{IAM_URL}/iam/v1/tokens'
        data = {'jwt': ServiceAccountAuth(sa_credentials).generate_jwt()}

        result = requests.post(url, params=data, headers=BASE_HEADERS)
        try:
            response = result.json()
        except json.decoder.JSONDecodeError:
            raise BadRequest(result.text)

        if not result.ok:
            raise BadRequest(result.text)
        if raw:
            return response
        return response.get('iamToken')

    @staticmethod
    def get_endpoints_from_api() -> dict:
        url = f'{BASE_URL}/endpoints'
        result = requests.get(url)
        response = result.json()

        if not result.ok:
            raise BadRequest(result.text)

        return response.get('endpoints')

    # Private methods for ComputeClient workflow

    def _delete_resource(self, url, await_complete=None) -> Operation:
        response = self._request.delete(url)
        operation = Operation.de_json(response, self)
        if not await_complete:
            return operation
        return OperationWait(operation).completed

    # actually, half-async (because Requests)
    async def _async_delete_resource(self, url) -> CoroutineType:
        response = self._request.delete(url)
        operation = Operation.de_json(response, self)

        await OperationWait(operation).await_complete_async()

    # # FIXME: useless?
    # def _run_operation(self, operation) -> Operation:
    #     return Operation.de_json(operation, self)

    def _resource_create(self, url, data=None, await_complete=True) -> Operation:
        response = self._request.post(url, json=data)
        operation = Operation.de_json(response, self)

        if not await_complete:
            return operation
        return OperationWait(operation).completed

    # actually, half-async (because Requests)
    async def _async_resource_create(self, url, data=None) -> Operation:
        response = self._request.post(url, json=data)
        operation = Operation.de_json(response, self)

        await OperationWait(operation).await_complete_async()

    # Operations public methods

    @log
    def operation(self, operation_id: str) -> Operation:
        url = f'{self.operation_url}/operations/{operation_id}'
        response = self._request.get(url)
        return Operation.de_json(response, self)

    @log
    def cancel_operation(self, operation_id: str) -> Operation:
        url = f'{self.operation_url}/operations/{operation_id}:cancel'
        try:
            response = self._request.post(url)
            return Operation.de_json(response, self)
        except YandexCloudError:
            raise BadRequest("Operation can't be canceled.")

    def cloud(self):
        pass

    def available_clouds(self):
        pass

    def update_cloud(self):
        pass

    def cloud_operations(self):
        pass

    def cloud_access_bindings(self):
        pass

    def update_cloud_access_bindings(self):
        pass

    def set_cloud_access_bindings(self):
        pass

    def folder(self):
        pass

    def folders_in_cloud(self):
        pass

    def folder_operations(self):
        pass

    def folder_access_bindings(self):
        pass

    def update_folder_access_bindings(self):
        pass

    def set_folder_access_bindings(self):
        pass

    def create_folder(self):
        pass

    def update_folder(self):
        pass

    def delete_folder(self):
        pass


    # Aliases

    getEndpoints = get_endpoints_from_api
    getIamToken = get_iam_token
    getServiceAccountToken = get_token_for_sa
    cancelOperation = cancel_operation


class ComputeClient(YandexCloudClient):
    """Yandex.Cloud Compute Client.

    Child class, which inherit the properties and methods
    from the YandexCloudClient parent class.

    Required Args:
      oauth_token: str
            or
      iam_token: str
            or
      service_account_key: dict

    Optional Args:
      request: Request
      base_url: str
      compute_url: str
      iam_url: str
      operation_url: str
      certificate_url: str
      certificate_data_url: str

    """

    def _instance_state_management(self, action=None, instance_id=None,
                                   await_complete=None) -> Operation:
        """Supported actions: start, restart, stop."""

        ACTIONS = ('start', 'restart', 'stop')
        if action not in ACTIONS:
            raise TypeError(f'Action {action} not supported')

        url = f'{self.compute_url}/compute/v1/instances/{instance_id}:{action}'
        response = self._request.post(url)
        operation = Operation.de_json(response, self)
        if not await_complete:
            return operation
        return OperationWait(operation).completed

    # actually, half-async (because Requests)
    async def _async_instance_state_management(self, action=None, instance_id=None) -> CoroutineType:
        """Supported actions: start, restart, stop."""

        ACTIONS = ('start', 'restart', 'stop')
        if action not in ACTIONS:
            raise TypeError(f'Action {action} not supported')

        url = f'{self.compute_url}/compute/v1/instances/{instance_id}:{action}'
        response = self._request.post(url)
        operation = Operation.de_json(response, self)

        await OperationWait(operation).await_complete_async()

    def _instance_disk_management(self, instance_id: str, data=None,
                                  action=None, await_complete=True) -> Operation:
        """Supported actions: detachDisk, attachDisk."""

        ACTIONS = ('detachDisk', 'attachDisk')
        if action not in ACTIONS:
            raise TypeError(f'Action {action} not supported')

        url = f'{self.compute_url}/compute/v1/instances/{instance_id}:{action}'
        response = self._request.post(url, json=data)
        operation = Operation.de_json(response, self)
        if not await_complete:
            return operation
        return OperationWait(operation).completed

    # actually, half-async (because Requests)
    async def _async_instance_disk_management(self, instance_id: str,
                                              action=None, data=None) -> Operation:
        """Supported actions: detachDisk, attachDisk."""

        ACTIONS = ('detachDisk', 'attachDisk')
        if action not in ACTIONS:
            raise TypeError(f'Action {action} not supported')

        url = f'{self.compute_url}/compute/v1/instances/{instance_id}:{action}'
        response = self._request.post(url, json=data)
        operation = Operation.de_json(response, self)

        await OperationWait(operation).await_complete_async()

    def _convert_attached_disks(self, disks: list) -> Disk:
        attached_disks = []
        for disk_id in disks:
            attached_disks.append(self.disk(disk_id, raw=True))
        return Disk.de_list(attached_disks, self)

    # Instance public methods

    @log
    def instance(self, instance_id: str, metadata=False) -> Instance:
        url = f'{self.compute_url}/compute/v1/instances/{instance_id}'
        if metadata:
            url += '?view=FULL'

        response = self._request.get(url)
        return Instance.de_json(response, self)

    @log
    def instances_in_folder(self, folder_id: str, page_size=1000, query_filter=None) -> [Instance]:
        url = f'{self.compute_url}/compute/v1/instances?folderId={folder_id}&pageSize={page_size}'
        if query_filter:
            url += f'&filter={query_filter}'
        response = self._request.get(url).get('instances')
        return Instance.de_list(response, self)

    @log
    def instance_serial_port_output(self, instance_id: str, port=1) -> str:
        url = f'{self.compute_url}/compute/v1/instances/{instance_id}:serialPortOutput?port={port}'
        response = self._request.get(url).get('contents')
        return response

    @log
    def instance_operations(self, instance_id: str, page_size=1000) -> [Operation]:
        url = f'{self.compute_url}/compute/v1/instances/{instance_id}/operations?pageSize={page_size}'
        response = self._request.get(url).get('operations')
        return Operation.de_list(response, self)

    @log
    def instance_attach_existent_disk(self, instance_id: str, disk_id: str, mode='READ_WRITE',
                                      device_name=None, auto_delete=False, await_complete=True,
                                      run_async_await=False) -> Operation:

        # prepare valid data for disk
        params = locals().copy()
        del params['self']
        data = {'attachedDiskSpec': AttachedDiskSpec.prepare(params, self)}

        if run_async_await:
            return self._async_instance_disk_management(instance_id,
                action='attachDisk', data=data)

        return self._instance_disk_management(instance_id, action='attachDisk',
            data=data, await_complete=await_complete)

    @log
    def instance_attach_new_disk(self, instance_id: str, size: int, mode='READ_WRITE',
                                 auto_delete=None, name=None, description=None, type_id=None,
                                 image_id=None, snapshot_id=None, device_name=None,
                                 await_complete=True, run_async_await=False) -> Operation:

        # prepare valid data for disk
        params = locals().copy()
        del params['self']
        data = {'attachedDiskSpec': AttachedDiskSpec.prepare(params, self)}

        if run_async_await:
            return self._async_instance_disk_management(instance_id,
                action='attachDisk', data=data)

        return self._instance_disk_management(instance_id, action='attachDisk',
            data=data, await_complete=await_complete)

    @log
    def instance_detach_disk(self, instance_id: str, disk_id=None, disk_name=None,
                             await_complete=True, run_async_await=False) -> Operation:
        if disk_id and disk_name:
            raise TooManyArguments('disk_id and disk_name received, but you can use only one param')

        if disk_id:
            data = {'diskId': disk_id}
        elif disk_name:
            data = {'diskName': disk_name}

        if run_async_await:
            return self._async_instance_disk_management(instance_id,
                action='detachDisk', data=data)

        return self._instance_disk_management(instance_id, action='detachDisk',
            data=data, await_complete=await_complete)

    @log
    def start_instance(self, instance_id: str, await_complete=True, run_async_await=False) -> Operation:
        if run_async_await:
            return self._async_instance_state_management(action='start',
                instance_id=instance_id)

        return self._instance_state_management(action='start',
            instance_id=instance_id, await_complete=await_complete)

    @log
    def restart_instance(self, instance_id: str, await_complete=True, run_async_await=False) -> Operation:
        if run_async_await:
            return self._async_instance_state_management(action='restart',
                instance_id=instance_id)

        return self._instance_state_management(action='restart',
            instance_id=instance_id, await_complete=await_complete)

    @log
    def stop_instance(self, instance_id: str, await_complete=True, run_async_await=False) -> Operation:
        if run_async_await:
            return self._async_instance_state_management(action='stop',
                instance_id=instance_id)

        return self._instance_state_management(action='stop',
            instance_id=instance_id, await_complete=await_complete)

    @log
    def delete_instance(self, instance_id: str, await_complete=True, run_async_await=False) -> Operation:
        url = self.compute_url + f'/compute/v1/instances/{instance_id}'
        if run_async_await:
            return self._async_delete_resource(url)
        return self._delete_resource(url, await_complete=await_complete)

    @log
    # FIXME: make better
    def create_instance(self, yaml_spec, await_complete=True,
                        run_async_await=False) -> Operation:
        """
        This method provide basic interface for creating instance in Compute Cloud.

        Currently support only from yaml params.

        Args:
          :yaml_spec: str `/path/to/file.yaml`
          :await_complete: bool
          :run_async_await: bool

        Metadata must be string.
        See: https://cloud.yandex.ru/docs/compute/concepts/vm-metadata

        For user-data use this example:
        ```
        user-data: |
          #cloud-config
          users:
          - name: akimrx
            sudo: ALL=(ALL) NOPASSWD:ALL
            shell: /bin/bash
            ssh-authorized-keys:
              - ssh-rsa AAA...
        ```
        """

        url = f'{self.compute_url}/compute/v1/instances'
        data = convert_yaml_to_dict(yaml_spec)

        if run_async_await:
            return self._async_resource_create(url, data=data)
        return self._resource_create(url, data=data, await_complete=await_complete)

    @log
    def update_instance(self):
        pass

    @log
    def update_instance_metadata(self):
        pass

    # Disks public methods

    @log
    def disk(self, disk_id: str, raw=False) -> Disk:
        url = f'{self.compute_url}/compute/v1/disks/{disk_id}'
        response = self._request.get(url)
        if raw:
            return response
        return Disk.de_json(response, self)

    @log
    def disk_operations(self, disk_id: str, page_size=1000) -> [Operation]:
        url = f'{self.compute_url}/compute/v1/disks/{disk_id}/operations?pageSize={page_size}'
        response = self._request.get(url).get('operations')
        return Operation.de_list(response, self)

    @log
    def disks_in_folder(self, folder_id: str, page_size=1000, query_filter=None) -> [Disk]:
        url = f'{self.compute_url}/compute/v1/disks?folderId={folder_id}&pageSize={page_size}'
        if query_filter:
            url += f'&filter={query_filter}'
        response = self._request.get(url).get('disks')
        return Disk.de_list(response, self)

    @log
    def delete_disk(self, disk_id: str, await_complete=True, run_async_await=False) -> Operation:
        url = f'{self.compute_url}/compute/v1/disks/{disk_id}'
        if run_async_await:
            return self._async_delete_resource(url)
        return self._delete_resource(url, await_complete=await_complete)

    @log
    def create_disk(self, folder_id: str, size: int, zone_id: str, name=None,
                    description=None, labels={}, type_id=None, image_id=None,
                    snapshot_id=None, await_complete=True, run_async_await=False) -> Operation:

        url = f'{self.compute_url}/compute/v1/disks'

        # Prepare valid data for new disk
        params = locals().copy()
        del params['self']
        data = DiskSpec.prepare(params, self)

        if run_async_await:
            return self._async_resource_create(url, data=data)
        return self._resource_create(url, data=data, await_complete=await_complete)

    @log
    def update_disk(self):
        pass

    # Snapshots public methods

    @log
    def snapshot(self, snapshot_id: str) -> Snapshot:
        url = f'{self.compute_url}/compute/v1/snapshots/{snapshot_id}'
        response = self._request.get(url)
        return Snapshot.de_json(response, self)

    @log
    def snapshot_operations(self, snapshot_id: str, page_size=1000) -> [Operation]:
        url = f'{self.compute_url}/compute/v1/snapshots/{snapshot_id}/operations?pageSize={page_size}'
        response = self._request.get(url).get('operations')
        return Operation.de_list(response, self)

    @log
    def snapshots_in_folder(self, folder_id: str, page_size=1000, query_filter=None) -> [Snapshot]:
        url = f'{self.compute_url}/compute/v1/snapshots?folderId={folder_id}&pageSize={page_size}'
        if query_filter:
            url += f'&filter={query_filter}'
        response = self._request.get(url).get('snapshots')
        return Snapshot.de_list(response, self)

    @log
    def create_snapshot(self, folder_id: str, disk_id: str, name=None, description=None,
                        labels=None, await_complete=True, run_async_await=False) -> Operation:
        url = f'{self.compute_url}/compute/v1/snapshots'

        params = locals().copy()
        del params['self']
        data = SnapshotSpec.prepare(params, self)

        if run_async_await:
            return self._async_resource_create(url, data=data)
        return self._resource_create(url, data=data, await_complete=await_complete)

    @log
    def delete_snapshot(self, snapshot_id: str, await_complete=True,
                        run_async_await=False) -> Operation:
        url = f'{self.compute_url}/compute/v1/snapshots/{snapshot_id}'

        if run_async_await:
            return self._async_delete_resource(url)
        return self._delete_resource(url, await_complete=await_complete)

    @log
    def update_snapshot(self):
        pass


    # Aliases

    startInstance = start_instance
    stopInstance = stop_instance
    restartInstance = restart_instance
    createInstance = create_instance
    deleteInstance = delete_instance
    updateInstance = update_instance
    updateInstanceMetadata = update_instance_metadata
    instanceSerialPortOut = instance_serial_port_output
    folderInstances = instances_in_folder
    instanceOperations = instance_operations
    instanceAttachNewDisk = instance_attach_existent_disk
    instanceAttachExistentDisk = instance_attach_existent_disk
    instanceDetachDisk = instance_detach_disk
    diskOperations = disk_operations
    folderDisks = disks_in_folder
    deleteDisk = delete_disk
    createDisk = create_disk
    updateDisk = update_disk
    snapshotOperations = snapshot_operations
    folderSnapshots = snapshots_in_folder
    createSnapshot = create_snapshot
    deleteSnapshot = delete_snapshot
    updateSnapshot = update_snapshot


class CertificateClient(YandexCloudClient):
    """Yandex.Cloud Certificate Manager Client.

    Child class, which inherit the properties and methods
    from the YandexCloudClient parent class.

    Required Args:
      oauth_token: str
            or
      iam_token: str
            or
      service_account_key: dict

    Optional Args:
      request: Request
      base_url: str
      compute_url: str
      iam_url: str
      operation_url: str
      certificate_url: str
      certificate_data_url: str

    """

    @log
    def certificate(self, certificate_id: str, view="FULL") -> Certificate:
        """Return certificate:
        BASIC - short info,
        FULL - full info with challenges.
        """
        url = f'{self.certificate_url}/certificate-manager/v1/certificates/{certificate_id}?view={view}'

        response = self._request.get(url)
        return Certificate.de_json(response, self)

    @log
    def certificate_content(self, certificate_id: str) -> CertificateContent:
        url = f'{self.certificate_data_url}/certificate-manager/v1/certificates/{certificate_id}:getContent'

        response = self._request.get(url)
        return CertificateContent.de_json(response, self)

    @log
    def certificates_in_folder(self,
                               folder_id: str,
                               page_size=1000,
                               query_filter=None,
                               view="BASIC") -> [Certificate]:
        """Return certificates in the specified folder:
        BASIC - short info,
        FULL - full info with challenges.
        """

        url = f'{self.certificate_url}/certificate-manager/v1/certificates?folderId={folder_id}&pageSize={page_size}&view={view}'
        if query_filter:
            url += f'&filter={query_filter}'
        response = self._request.get(url).get('certificates')
        return Certificate.de_list(response, self)

    @log
    def certificate_operations(self,
                               certificate_id: str,
                               page_size=1000) -> [Operation]:
        url = f'{self.compute_url}/certificate-manager/v1/certificates{certificate_id}/operations?pageSize={page_size}'
        response = self._request.get(url).get('operations')
        return Operation.de_list(response, self)

    @log
    def create_user_certificate(self):
        pass

    @log
    def request_new_letsencrypt_certificate(self,
                                            folder_id: str,
                                            name: str,
                                            domains: list,
                                            description: str = None,
                                            labels: dict = dict(),
                                            challenge_type: str = "DNS",
                                            await_complete=True,
                                            run_async_await=False) -> Operation:
        """Create new Let's encrypt free certificate in the specified folder.
        Challenge type must be DNS or HTTP.
        """

        url = f'{self.certificate_url}/certificate-manager/v1/certificates/requestNew'

        params = locals().copy()
        del params['self']
        data = CertificateRequestSpec.prepare(params, self)

        if run_async_await:
            return self._async_resource_create(url, data=data)
        return self._resource_create(url, data=data, await_complete=await_complete)

    @log
    def update_certificate(self,
                           certificate_id: str,
                           updateMask: str,
                           name=None,
                           description=None,
                           labels=None,
                           certificate=None,
                           chain=None,
                           private_key=None) -> Operation:
        pass

    @log
    def delete_certificate(self,
                           certificate_id: str,
                           await_complete=True,
                           run_async_await=False) -> Operation:
        url = f'{self.certificate_url}/certificate-manager/v1/certificates/{certificate_id}'

        if run_async_await:
            return self._async_delete_resource(url)
        return self._delete_resource(url, await_complete=await_complete)


    # Aliases

    folderCertificates = certificates_in_folder
    certificateContent = certificate_content
    certificateOperations = certificate_operations
    createUserCertificate = create_user_certificate
    createLetsEncryptCertificate = request_new_letsencrypt_certificate
    updateCertificate = update_certificate
    deleteCertificate = delete_certificate
