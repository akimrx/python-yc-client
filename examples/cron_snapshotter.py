"""This module is an example of automatic disk snapshot management."""
#!/usr/bin/env python3

import time
import logging
import asyncio
import argparse

from pathlib import Path

import yaml

from yandex_cloud_client import ComputeClient
from yandex_cloud_client.error import YandexCloudError


HOMEDIR = Path.home()
BASE_CONFIG_PATH = HOMEDIR.joinpath(".config", "yc-client", "snapshotter.yaml")


class Config(object):
    """This object represents a settings for snapshotter example.

    YAML example (path: ~/.config/yc-client/snapshotter.yaml):

    token: AQAAAAA....
    lifetime: 6  # days
    labels:
      created_by: script
    graceful: true
    with_secondary: true
    instances:
    - efqwe123qwe123qwe123
    - efzxc456zxc456zxc456

    """

    def __init__(self, filepath: str = None):
        self.filepath = filepath or BASE_CONFIG_PATH
        self.token = None
        self.lifetime = 365
        self.instances = []
        self.labels = {"created_by": "script"}
        self.loglevel = args.loglevel or "INFO"
        self.graceful = False
        self.with_secondary = False

        self.__build()

    def __read(self):
        try:
            with open(self.filepath, "r") as cfgfile:
                data = yaml.load(cfgfile, Loader=yaml.Loader)
                return data
        except FileNotFoundError:
            raise YandexCloudError(
                f"Config file not found. Please, specify config path: '--config-file <filepath>' " \
                f"or create a default file by path: {BASE_CONFIG_PATH}"
            )
        except TypeError:
            raise YandexCloudError(f"Corrupted config file or bad format. Please, verify your config file: {self.filepath}")

    def __build(self):
        if self.filepath is None:
            return

        config = self.__read()
        if config is None or not config:
            return

        for key, value in config.items():
            if key.lower() == "loglevel":
                value = value.upper()
            setattr(self, key, value)


parser = argparse.ArgumentParser(
    prog="yc-snapshotter",
    description="Simple script for automatic create/clean YC snapshots",
    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=90),
    add_help=False
)

# Commands
commands = parser.add_argument_group("Arguments")
commands.add_argument(
    "-a", "--all",
    action="store_true",
    required=False,
    help="Run create and delete tasks"
)
commands.add_argument(
    "-c", "--create",
    action="store_true",
    required=False,
    help="Run create snapshots task"
)
commands.add_argument(
    "-d", "--delete",
    action="store_true",
    required=False,
    help="Run delete snapshots task"
)

# Options
options = parser.add_argument_group("Options")
options.add_argument(
    "-S", "--with-secondary",
    action="store_true",
    required=False,
    help="Runs the tasks the same way for secondary disks"
)
options.add_argument(
    "-G", "--graceful",
    action="store_true",
    required=False,
    help="Graceful snapshot creation. First disables the VM and turns it on after the operation is completed"
)

options.add_argument(
    "-C", "--config-file",
    metavar="file",
    type=str,
    required=False,
    help="Path to the config file"
)
options.add_argument(
    "--loglevel",
    metavar="debug/info/warning/error",
    type=str,
    help="Log facility. Default: info"
)
options.add_argument(
    "--help",
    action="help",
    help="Show this help message"
)
options.add_argument(
    "--version",
    action="version",
    version="v0.1",
    help="Show example version"
)

args = parser.parse_args()
config = Config(args.config_file or BASE_CONFIG_PATH)
compute = ComputeClient(oauth_token=config.token)
logging.basicConfig(
    level=config.loglevel,
    datefmt="%d %b %H:%M:%S",
    format=" %(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



async def snapshot_cleaner(instance_id: str, with_secondary: bool = False):
    """Delete all disk snapshots with special labels for instance.

    Arguments:
      :instance_id: str - instance for disk snapshots search
      :with_secondary: bool - delete snapshots for secondary disks

    """

    instance = compute.instance(instance_id)
    logger.info(f"Searching snapshots older {config.lifetime} days for {instance.name} {instance.id}")

    for snapshot in instance.boot_disk.snapshots():
        if all(label in snapshot.labels.items() for label in config.labels.items()):
            if snapshot.age >= config.lifetime:
                logger.info(
                    f"Delete snapshot {snapshot.name} from secondary disk " \
                    f"id {instance.boot_disk.id} attached to {instance.name}"
                )
                await snapshot.delete(run_async_await=True)
                logger.info(f"Snapshot {snapshot.name} deleted")

    if with_secondary:
        for disk in instance.secondary_disks:
            for snapshot in disk.snapshots():
                if all(label in snapshot.labels.items() for label in config.labels.items()):
                    if snapshot.age < config.lifetime:
                        logger.info(
                            f"Delete snapshot {snapshot.name} from secondary disk " \
                            f"id {instance.boot_disk.id} attached to {instance.name}"
                        )
                        await snapshot.delete(run_async_await=True)
                        logger.info(f"Snapshot {snapshot.name} deleted")


async def snapshot_spawner(instance_id: str, graceful: bool = False, with_secondary: bool = False):
    """Create boot disk snapshot for instance."""
    instance = compute.instance(instance_id)
    logger.info(f"Prepare instance {instance.name} {instance.id} for snapshotting.")
    need_start = False

    if graceful and not instance.stopped:
        need_start = True
        logger.info(f"Stopping instance {instance.name}")
        await instance.stop(run_async_await=True)

    logger.info(
        f"Creating {'graceful' if graceful else 'force'} snapshot " \
        f"for boot disk {instance.boot_disk.id} attached to {instance.name}"
    )
    snapshot_name = f"{instance.name}-boot-{int(time.time())}"
    await instance.boot_disk.create_snapshot(run_async_await=True, name=snapshot_name, labels=config.labels)
    logger.info(f"Snapshot for boot disk {instance.boot_disk.id} attached to {instance.name} created.")

    if with_secondary:
        for disk in instance.secondary_disks:
            snapshot_name = f"{instance.name}-secondary-{int(time.time())}"
            await disk.create_snapshot(run_async_await=True, name=snapshot_name, labels=config.labels)
            logger.info(f"Snapshot for secondary disk {disk.id} attached to {instance.name} created.")

    if graceful and need_start:
        logger.info(f"Starting instance {instance.name}")
        await instance.start(run_async_await=True)

    logging.info(f"{instance.name}, {instance.id}, {instance.status}")


def run_cleaner():
    """Run snapshot cleaner for instance list."""
    tasks = [
        snapshot_cleaner(
            instance_id,
            with_secondary=args.with_secondary or config.with_secondary
        )
        for instance_id in config.instances
    ]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


def run_spawner():
    """Run snapshot spawner (creater) for instance list."""
    tasks = [
        snapshot_spawner(
            instance_id,
            graceful=args.graceful or config.graceful,
            with_secondary=args.with_secondary or config.with_secondary
        )
        for instance_id in config.instances
    ]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


def main(all_tasks: bool = False, delete: bool = False, create: bool = False):
    if all_tasks:
        run_cleaner()
        run_spawner()
        return

    if delete:
        run_cleaner()

    if create:
        run_spawner()


if __name__ == "__main__":
    main(all_tasks=args.all, create=args.create, delete=args.delete)
