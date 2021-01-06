"""This module is an example of automatic run stopped instances."""
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
    interval: 15  # seconds
    loglevel: info
    instances:
    - efqwe123qwe123qwe123
    - efzxc456zxc456zxc456

    """

    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.token = args.token or None
        self.interval = args.interval if args.interval is not None else 60
        self.instances = args.instances.split(",") if args.instances else []
        self.loglevel = args.loglevel or "INFO"

        self.__required_params__ = (self.token, self.interval, self.instances)
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
    prog="yc-watchdog",
    description="Simple script for automatic start preemptible instances",
    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=90),
    add_help=False
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
    "-I", "--interval",
    type=int,
    metavar="int",
    required=False,
    help="Interval for checkout instance state (in seconds). Default: 60"
)
params.add_argument(
    "-i", "--instances",
    type=str,
    metavar="str [, ...]",
    required=False,
    help="Comma separated instances"
)

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


args = parser.parse_args()
config = Config(args.config_file)
compute = ComputeClient(oauth_token=config.token)
logging.basicConfig(
    level=config.loglevel.upper(),
    datefmt="%d %b %H:%M:%S",
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def remove_invalid_instances():
    logger.debug("Validating instances...")
    instances = []
    for i, instance_id in enumerate(config.instances):
        try:
            instance = compute.instance(instance_id)
            instances.append(instance)
        except Exception as err:
            logging.error(err)
            config.instances.pop(i)

    return instances


async def start_instance(instance_id):
    instance = compute.instance(instance_id)
    if instance.stopped:
        logger.info(f"Instance {instance.name} (id: {instance.id}) stopped. Starting...")
        await instance.start(run_async_await=True)
        logger.info(f"Instance {instance.name} has been started")
    else:
        logger.debug(f"Unsuitable instance state: {instance.status.lower()}. Skipping...")


def prepare_tasks():
    tasks = [
        start_instance(instance_id)
        for instance_id in config.instances
    ]
    logger.debug(f"Created {len(tasks)} tasks for checkout instance state")
    return asyncio.gather(*tasks)


def main():
    logger.info(f"Watchdog is started... [checkout interval set to {config.interval} seconds]")
    while True:
        remove_invalid_instances()
        logger.debug("Preparing tasks...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(prepare_tasks())
        logger.debug("Tasks completed. Sleeping...")
        time.sleep(int(config.interval))
    loop.close()


if __name__ == "__main__":
    main()
