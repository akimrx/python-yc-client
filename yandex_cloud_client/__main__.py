#!/usr/bin/env python3
# pylint: disable=E0401, C0114

import subprocess
import sys
from typing import Optional

import certifi

from . import __version__ as client_ver


def _git_revision() -> Optional[str]:
    try:
        output = subprocess.check_output(["git", "describe", "--long", "--tags"], stderr=subprocess.STDOUT)
    except (subprocess.SubprocessError, OSError):
        return None
    return output.decode().strip()


def print_ver_info() -> None:
    git_revision = _git_revision()
    print('yandex-cloud-client {}'.format(client_ver) + (' ({})'.format(git_revision) if git_revision else ''))
    print('certifi {}'.format(certifi.__version__))  # type: ignore[attr-defined]
    print('Python {}'.format(sys.version.replace('\n', ' ')))


def main() -> None:
    print_ver_info()


if __name__ == '__main__':
    main()
