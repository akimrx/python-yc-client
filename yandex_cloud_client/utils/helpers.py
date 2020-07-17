#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains helper functions."""

import re
import yaml
import json
import datetime as dt


def disk_mode_converter(mode):
    modes = {
        'ro': 'READ_ONLY',
        'rw': 'READ_WRITE'
    }

    key = mode.lower()
    return modes.get(key, mode)


def convert_yaml_to_dict(data: yaml):
    with open(data, 'r') as infile:
        result = yaml.load(infile, Loader=yaml.Loader)
    infile.close()

    return result


def convert_camel_to_snake(text: str):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def universal_obj_hook(obj: [list, dict]):
    if isinstance(obj, list):
        result = []
        for i in obj:
            result.append(_object_hook(i))
        return result

    elif isinstance(obj, dict):
        return _object_hook(obj)

    return obj


def _object_hook(obj: dict):
    cleaned_object = {}
    for key, value in obj.items():
        key = convert_camel_to_snake(key.replace('-', '_'))

        if len(key) and key[0].isdigit():
            key = '_' + key

        cleaned_object.update({key: value})
    return cleaned_object


def human_readable_size(raw_bytes, granularity=2):
    result = []
    sizes = (
        ('TB', 1024**4),
        ('GB', 1024**3),
        ('MB', 1024**2),
        ('KB', 1024),
        ('B', 1)
    )
    if raw_bytes == 0:
        return 0
    else:
        for name, count in sizes:
            value = raw_bytes // count
            if value:
                raw_bytes -= value * count
                result.append(f'{value} {name}')
        return ', '.join(result[:granularity])


def from_timestamp(unixtime):
    readable = dt.datetime.utcfromtimestamp(unixtime).isoformat()
    return readable


def string_to_datetime(strtime):
    try:
        return dt.datetime.strptime(strtime, '%Y-%m-%dT%H:%M:%Sz')
    except Exception:
        return strtime


def generate_instance_yaml_example(path=None):
    filename = 'instance_example.yaml'
    if path is not None:
        if path.endswith('/'):
            path.strip('/')
        filename = f'{path}/instance_example.yaml'

    with open(filename, 'w') as outfile:
        yaml.dump(instance_dict_example(), outfile, sort_keys=False)
    outfile.close()
    print('File "instance_example.yaml" saved.')


def instance_dict_example():
    example = {
        "folderId": "string",
        "name": "string",
        "description": "string",
        "labels": "object",
        "zoneId": "string",
        "platformId": "string",
        "resourcesSpec": {
            "memory": "string",
            "cores": "string",
            "coreFraction": "string",
            "gpus": "string"
        },
        "metadata": "object",
        "bootDiskSpec": {
            "mode": "string",
            "deviceName": "string",
            "autoDelete": False,
            # `bootDiskSpec` includes only one of the fields `diskSpec`, `diskId`
            "diskSpec": {
                "name": "string",
                "description": "string",
                "typeId": "string",
                "size": "string",
            # `bootDiskSpec.diskSpec` includes only one of the fields `imageId`, `snapshotId`
            "imageId": "string",
            "snapshotId": "string",
            # end of the list of possible fields`bootDiskSpec.diskSpec`
            },
            "diskId": "string",
            # end of the list of possible fields`bootDiskSpec`
        },
        "secondaryDiskSpecs": [
            {
                "mode": "string",
                "deviceName": "string",
                "autoDelete": False,
                # `secondaryDiskSpecs[]` includes only one of the fields `diskSpec`, `diskId`
                "diskSpec": {
                    "name": "string",
                    "description": "string",
                    "typeId": "string",
                    "size": "string",
                    # `secondaryDiskSpecs[].diskSpec` includes only one of the fields `imageId`, `snapshotId`
                    "imageId": "string",
                    "snapshotId": "string",
                    # end of the list of possible fields`secondaryDiskSpecs[].diskSpec`
                },
            "diskId": "string",
            # end of the list of possible fields`secondaryDiskSpecs[]`
            }
        ],
        "networkInterfaceSpecs": [
            {
                "subnetId": "string",
                "primaryV4AddressSpec": {
                    "address": "string",
                    "oneToOneNatSpec": {
                        "ipVersion": "string",
                        "address": "string"
                    }
                },
                "primaryV6AddressSpec": {
                    "address": "string",
                    "oneToOneNatSpec": {
                        "ipVersion": "string",
                        "address": "string"
                    }
                }
            }
        ],
        "hostname": "string",
        "schedulingPolicy": {
            "preemptible": False
        },
        "serviceAccountId": "string",
        "networkSettings": {
            "type": "string"
        },
        "placementPolicy": {
            "placementGroupId": "string"
        }
    }

    return example
