"""This module is an example of automatic disk snapshot management."""
#!/usr/bin/env python3

import sys
import time
import logging
import asyncio
import argparse

import yaml

from yandex_cloud_client import ComputeClient
from yandex_cloud_client.error import YandexCloudError


class Config(object):
    """This object represents a settings for snapshotter example.

    YAML example:

    token: AQAAAAA....
    lifetime: 6  # days
    labels:
      creator: snapshotter
    graceful: true
    with_secondary: true
    instances:
    - efqwe123qwe123qwe123
    - efzxc456zxc456zxc456

    """

    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.token = args.token or None
        self.lifetime = args.lifetime if args.lifetime is not None else 365
        self.instances = []
        self.labels = {"creator": "snapshotter"}
        self.loglevel = args.loglevel or "INFO"
        self.graceful = False
        self.with_secondary = False

        self.__required_params__ = (self.token, self.lifetime, self.instances)
        self.__build_from_file()
        self.__verify()

    def __read(self):
        try:
            with open(self.filepath, "r") as cfgfile:
                data = yaml.load(cfgfile, Loader=yaml.Loader)
                return data
        except FileNotFoundError:
            raise YandexCloudError(
                f"Config file not found. Please, specify config path: '--config-file <filepath>' "
            )
        except TypeError:
            raise YandexCloudError(
                f"Corrupted config file or bad format. Please, verify your config file: {self.filepath}"
            )

    def __build_from_file(self):
        if all(self.__required_params__):
            return
        if self.filepath is None:
            return

        config = self.__read()
        if config is None or not config:
            return

        for key, value in config.items():
            if key.lower() == "loglevel":
                value = value.upper()
            setattr(self, key, value)

    def __verify(self):
        if self.token is None:
            raise YandexCloudError("OAuth token is empty. Please, pass the token by arg '--token' or use config file")
        elif not self.instances or self.instances is None:
            raise YandexCloudError("List of instances is empty. Nothing to do")


parser = argparse.ArgumentParser(
    prog="yc-snapshotter",
    description="Simple script for automatic create/clean YC snapshots",
    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=90),
    add_help=False
)

# Commands
commands = parser.add_argument_group("Commands")
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

params = parser.add_argument_group("Parameters")
params.add_argument(
    "-t", "--token",
    type=str,
    metavar="str",
    required=False,
    help="Yandex.Cloud OAuth token"
)
params.add_argument(
    "-l", "--lifetime",
    type=int,
    metavar="int",
    required=False,
    help="Age of the snapshot to delete. Default: 365"
)

# Options
options = parser.add_argument_group("Options")
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
    "-E", "--get-config-example",
    action="store_true",
    required=False,
    help="Show example config"
)
options.add_argument(
    "--version",
    action="version",
    version="v0.1",
    help="Show version"
)

args = parser.parse_args()


def print_config_example():
    msg = """
token: AQAAAisahdsal...
loglevel: info

global_options:
  lifetime: 6
  graceful: true
  with_secondary: false
  watch_all_snapshots: false

instances:
  - id: qwe123qwe123qweW
    with_secondary: true
    min_snapshots: 1
    max_snapshots: 2
    watch_all_snapshots: true

  - id: zxc456zxc456zxcX
    graceful: false
    lifetime: 14
    min_snapshots: 2
    max_snapshots: 10
"""
    print(msg)
    sys.exit(0)


if args.get_config_example:
    print_config_example()

OP_TIMEOUT = 900
config = Config(args.config_file)
compute = ComputeClient(oauth_token=config.token, operation_timeout=OP_TIMEOUT)
logging.basicConfig(
    level=config.loglevel.upper(),
    datefmt="%d %b %H:%M:%S",
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

CONCURRENT_OP_QUOTA = 15
OP_LIMIT = round(CONCURRENT_OP_QUOTA / len(config.instances))
if OP_LIMIT <= 1:
    OP_LIMIT = 3


# TODO: finish
class InstanceParams(object):
    """Not completed."""
    def __init__(
        self,
        id=None,
        min_snapshots=None,
        max_snapshots=None,
        watch_all_snapshots=None,
        graceful=None,
        lifetime=None,
        with_secondary=None
    ):
        self.id = id
        self.min_snapshots = min_snapshots or 1
        self.max_snaphosts = max_snaphosts or 999
        self.watch_all_snapshots = watch_all_snapshots or config.watch_all_snapshots or False
        self.graceful = graceful or config.graceful or True
        self.lifetime = lifetime or config.lifetime or 365
        self.with_secondary = with_secondary or config.with_secondary or False


def list_chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def remove_invalid_instances():
    logger.info("Validating instances...")
    instances = []
    for i, instance_id in enumerate(config.instances):
        try:
            instance = compute.instance(instance_id)
            instances.append(instance)
        except Exception as err:
            logging.error(err)
            config.instances.pop(i)

    return instances


async def snapshot_cleaner(instance_id: str, with_secondary: bool = False):
    """Delete all disk snapshots with special labels for instance.

    Arguments:
      :instance_id: str - instance for disk snapshots search
      :with_secondary: bool - delete snapshots for secondary disks

    """

    instance = compute.instance(instance_id)
    todo_list = []
    logger.info(f"Searching snapshots older {config.lifetime} days for {instance.name} (id: {instance.id})")

    for snapshot in instance.boot_disk.snapshots():
        if not all(label in snapshot.labels.items() for label in config.labels.items()):
            continue
        if snapshot.age < config.lifetime:
            continue
        logger.info(
            f"Prepare a deletion operation for snapshot {snapshot.name} of the boot disk " \
            f"id {instance.boot_disk.id} attached to {instance.name}"
        )
        todo_list.append(snapshot.delete(run_async_await=True))

    if with_secondary:
        for disk in instance.secondary_disks:
            for snapshot in disk.snapshots():
                if not all(label in snapshot.labels.items() for label in config.labels.items()):
                    continue
                if snapshot.age < config.lifetime:
                    continue
                logger.info(
                    f"Prepare a deletion operation for snapshot {snapshot.name} of the secondary disk " \
                    f"id {instance.boot_disk.id} attached to {instance.name}"
                )
                todo_list.append(snapshot.delete(run_async_await=True))

    if not todo_list:
        logger.info(
            f"Snapshots of the {instance.name} disk that fall under the specified conditions were not found"
        )
    else:
        # Concurrent operations quota bypass
        if len(todo_list) > OP_LIMIT:
            logger.info(
                f"The number of prepared operations of deleting a snapshot is more than limit ({OP_LIMIT}). " \
                f"Splitting tasks into chunks to bypass the quota for concurrent operations")
            for i, chunk in enumerate(list_chunks(todo_list, OP_LIMIT)):
                logger.info(
                    f"Deleting a disk snapshots of instance {instance.name}... [chunk {i + 1}]"
                )
                await asyncio.gather(*chunk)
        else:
            logger.info(f"Deleting a disk snapshots of instance {instance.name}")
            await asyncio.gather(*todo_list)

        logger.info(
            f"Total deleted the instance {instance.name} (id: {instance.id}) " \
            f"snapshots: {len(todo_list)}"
        )


async def snapshot_spawner(instance_id: str, graceful: bool = False, with_secondary: bool = False):
    """Create boot disk snapshot for instance."""
    instance = compute.instance(instance_id)
    logger.info(
        f"Prepare the instance {instance.name} (id: {instance.id}, state: {instance.status}) " \
        f"for snapshotting"
    )
    need_start = False
    todo_list = []

    if graceful and not instance.stopped:
        need_start = True
        logger.info(f"Stopping instance {instance.name}")
        await instance.stop(run_async_await=True)

    logger.info(
        f"Prepare a {'graceful' if graceful else 'force'} operation for create snapshot " \
        f"of boot disk {instance.boot_disk.id} attached to {instance.name}"
    )
    snapshot_name = f"{instance.name}-boot-{int(time.time())}"
    todo_list.append(
        instance.boot_disk.create_snapshot(
            run_async_await=True,
            name=snapshot_name,
            labels=config.labels
        )
    )

    if with_secondary:
        for disk in instance.secondary_disks:
            logger.info(
                f"Prepare a {'graceful' if graceful else 'force'} operation for create snapshot " \
                f"of secondary disk {disk.id} attached to {instance.name}"
            )
            snapshot_name = f"{instance.name}-secondary-{disk.id}-{int(time.time())}"
            todo_list.append(
                disk.create_snapshot(
                    run_async_await=True,
                    name=snapshot_name,
                    labels=config.labels
                )
            )

    # Concurrent operations quota bypass
    if len(todo_list) > OP_LIMIT:
        logger.info(
            "The number of prepared operations for creating a snapshot is more than limit ({OP_LIMIT}). " \
            "Splitting tasks into chunks to bypass the quota for concurrent operations"
        )
        for i, chunk in enumerate(list_chunks(todo_list, OP_LIMIT)):
            logger.info(
                f"Creating a disk snapshots of instance {instance.name}... [chunk {i + 1}]"
            )
            await asyncio.gather(*chunk)
    else:
        logger.info(f"Creating a disk snapshots of instance {instance.name}... ")
        await asyncio.gather(*todo_list)

    if graceful and need_start:
        logger.info(f"Starting instance {instance.name}")
        await instance.start(run_async_await=True)

    logging.info(
        f"Total created snapshots for {instance.name} (id: {instance.id}): {len(todo_list)}. " \
        f"Instance status: {instance.status}"
    )


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
    loop.run_until_complete(asyncio.gather(*tasks))


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
    loop.run_until_complete(asyncio.gather(*tasks))


def main(all_tasks: bool = False, delete: bool = False, create: bool = False):
    remove_invalid_instances()

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
