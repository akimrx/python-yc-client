#!/usr/bin/env python3

import os
import json

# Declaring constants
HOMEDIR = os.path.expanduser('~')
CONFIGPATH = os.path.join(HOMEDIR, '.config', 'yc-client')
INSTANCE_SPEC = '/path/to/instance_example.yaml'

# Init ComputeClient with service account
from yandex_cloud_client import ComputeClient

with open(f'{CONFIGPATH}/key.json', 'r') as infile:
    credentials = json.load(infile)

compute = ComputeClient(service_account_key=credentials)


def create_new_instance(yaml_spec):
    """Create new instance and return instance ID."""
    create_operation = compute.create_instance(yaml_spec)
    if create_operation.completed:
        print('New instance created with ID:', create_operation.metadata.instance_id)
        return create_operation.metadata.instance_id


def get_instance_and_delete(instance_id):
    """Print instance attr and delete."""
    instance = compute.instance(instance_id, metadata=True)
    print('Instance IP:', instance.network_interfaces[0].primary_v4_address.one_to_one_nat.address)
    print('User metadata:', instance.metadata)
    print('Status:', instance.status)

    if instance.delete().completed:
        print('Instance deleting finished!')


if __name__ == '__main__':
    new_instance = create_new_instance(INSTANCE_SPEC)
    get_instance_and_delete(new_instance)