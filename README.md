# Unofficial Yandex.Cloud REST API Client

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**PRE-ALPHA VERSION**  

**Probably, this REST API Client will make your life with Yandex.Cloud a little easier.**  

## Installing

You  can install from source with:

```bash
git clone https://github.com/akimrx/python-yc-client  --recursive
cd python-yc-client 
python3 setup.py install
```

## Getting started

### Client and authorization

The first step is to import required client of the Yandex.Cloud Services.  
Each client of a Yandex.Cloud service inherits authorization from the base client, which supports three methods:

* OAuth token

```python
from yandex_cloud_client import ComputeClient

client = ComputeClient(oauth_token='YOUR_OAUTH_TOKEN')
```

* IAM token

```python
from yandex_cloud_client import ComputeClient

client = ComputeClient(iam_token='YOUR_IAM_TOKEN')
```

* Service account key

```python
import json
from yandex_cloud_client import ComputeClient

with open('/path/to/key.json', 'r') as infile:
    credentials = json.load(infile)

client = ComputeClient(service_account_key=credentials)
```

### Basic example for Instance from Compute Cloud Service

```python
from yandex_cloud_client import ComputeClient

compute = ComputeClient(oauth_token='YOUR_OAUTH_TOKEN')


def show_instance_and_restart(instance_id):
    instance = compute.instance(instance_id, metadata=True)
    print('Name:', instance.name)
    print('Cores:', instance.resources.cores)
    print('Memory:', instance.resources.memory)
    print('SSH-keys:', instance.metadata.ssh_keys)

    if instance.running:
        operation = instance.restart()
        if operation.completed:
            print(f'Instance {instance.name} restarted!')

    print('Current instance state:', instance.status)


def boot_disk_snapshot(instance_id):
    instance = compute.instance(instance_id)

    if not instance.stopped:  # also, you can use instance.status != 'STOPPED'
        print('Stopping instance..')
        instance.stop()

    print('Creating snapshot for boot disk..')
    instance.boot_disk.create_snapshot()
    print('Starting instance without awaiting complete.')
    instance.start(await_complete=False)



if __name__ == '__main__':
    show_instance_and_restart('YOUR_INSTANCE_ID')
    boot_disk_snapshot('YOUR_INSTANCE_ID')
```

### Logging

This library uses the `logging` module.

Example of usage:

```python
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)
```

### Borrowed arch design

The client was written under the inspiration of architecture design:  
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)  
* [yandex-music-api](https://github.com/MarshalX/yandex-music-api)  