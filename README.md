# Unofficial Yandex.Cloud REST API Client

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

![](docs/logo.png =200px)

**PRE-ALPHA VERSION**  

**Probably, this REST API Client will make your life with Yandex.Cloud a little easier.**  

## Installing

* Installing from pypi:
```bash
pip3 install yandex-cloud-client
```
  
* Also, you can install from source with:

```bash
git clone https://github.com/akimrx/python-yc-client  --recursive
cd python-yc-client 
make install
```
  
or
  
```bash
git clone https://github.com/akimrx/python-yc-client  --recursive
cd python-yc-client 
python3 setup.py install
```

## Getting started

### Client and authorization

The first step is to import required client of the Yandex.Cloud Services.  
Each client of a Yandex.Cloud service inherits authorization from the base client, which supports three methods:

* [OAuth token](https://oauth.yandex.com/authorize?response_type=token&client_id=1a6990aa636648e9b2ef855fa7bec2fb)

```python
from yandex_cloud_client import ComputeClient

client = ComputeClient(oauth_token='YOUR_OAUTH_TOKEN')
```

* [IAM token](https://cloud.yandex.com/docs/iam/operations/iam-token/create)

```python
from yandex_cloud_client import ComputeClient

client = ComputeClient(iam_token='YOUR_IAM_TOKEN')
```

* [Service account key](https://cloud.yandex.com/docs/iam/operations/authorized-key/create)

```python
import json
from yandex_cloud_client import ComputeClient

with open('/path/to/key.json', 'r') as infile:
    credentials = json.load(infile)

client = ComputeClient(service_account_key=credentials)
```

> You can get key.json from [Yandex Cloud CLI](https://cloud.yandex.com/docs/cli/quickstart)
> `yc iam key create --service-account-name my-robot -o my-robot-key.json`

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