"""This module is an example of automatic disk snapshot management."""
#!/usr/bin/env python3

import os
import time
import yaml
import logging
import asyncio

from yandex_cloud_client import ComputeClient
from yandex_cloud_client.error import YandexCloudError

logging.basicConfig(level=logging.INFO, datefmt='%d %b %H:%M:%S', format=' %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HOMEDIR = os.path.expanduser('~')
CONFIGFILE = os.path.join(HOMEDIR, '.config', 'yc-client', 'snapshotter.yaml')


class Config:
    """This object represents a settings for snapshotter example.

    YAML example (path: ~/.config/yc-client/snapshotter.yaml):

    token: AQAAAAA....
    lifetime: 6  # days
    instances:
    - efqwe123qwe123qwe123
    - efzxc456zxc456zxc456

    """

    try:
        with open(CONFIGFILE, 'r') as configfile:
            config = yaml.load(configfile, Loader=yaml.Loader)
    except FileNotFoundError:
        raise YandexCloudError(f'Config file for snapshotter not found. Please, check the config: {CONFIGFILE}')
    except TypeError:
        raise YandexCloudError('Corrupted config file or bad format.')

    TOKEN = config.get('token')
    SNAPSHOT_LIFETIME = config.get('lifetime') or 365
    INSTANCES = config.get('instances')

    if TOKEN is None:
        raise YandexCloudError(f'OAuth token for snapshotter is empty. Check the config file: {CONFIGFILE}')

    if not INSTANCES:
        raise YandexCloudError('Instance list is empty. Nothing to do.')


compute = ComputeClient(oauth_token=Config.TOKEN)


async def snapshot_cleaner(instance_id: str):
    """Delete all boot disk snapshots for instance."""
    instance = compute.instance(instance_id)
    logger.info(f'Searching snapshots older {Config.SNAPSHOT_LIFETIME} days for {instance.name} {instance.id}')

    for snapshot in instance.boot_disk.snapshots():
        if snapshot.age >= Config.SNAPSHOT_LIFETIME:
            logger.info(f'Delete snapshot {snapshot.name} from source boot disk id {instance.boot_disk.id} attached to {instance.name}')
            await snapshot.delete(run_async_await=True)
            logger.info(f'Snapshot {snapshot.name} deleted')


async def snapshot_spawner(instance_id: str):
    """Create boot disk snapshot for instance."""
    instance = compute.instance(instance_id)
    logger.info(f'Prepare instance {instance.name} {instance.id} for snapshotting.')
    need_start = False

    if not instance.stopped:
        need_start = True
        logger.info(f'Stopping instance {instance.name}')
        await instance.stop(run_async_await=True)

    logger.info(f'Creating snapshot for boot disk {instance.boot_disk.id} attached to {instance.name}')
    snapshot_name = f'{instance.name}-{int(time.time())}'
    await instance.boot_disk.create_snapshot(run_async_await=True, name=snapshot_name)
    logger.info(f'Snapshot for boot disk {instance.boot_disk.id} attached to {instance.name} created.')

    if need_start:
        logger.info(f'Starting instance {instance.name}')
        await instance.start(run_async_await=True)

    logging.info(f'{instance.name}, {instance.id}, {instance.status}')


def run_cleaner():
    """Run snapshot cleaner for instance list."""
    tasks = [snapshot_cleaner(instance_id) for instance_id in Config.INSTANCES]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


def run_spawner():
    """Run snapshot spawner (creater) for instance list."""
    tasks = [snapshot_spawner(instance_id) for instance_id in Config.INSTANCES]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


def main(clean=False, create=False):
    if clean:
        run_cleaner()
    if create:
        run_spawner()


if __name__ == '__main__':
    main(create=True, clean=True)
