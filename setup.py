#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
from setuptools import setup, find_packages

cwd = path.abspath(path.dirname(__file__))

def readme():
    with open("README.md", "r") as fh:
        long_description = fh.read()

    return long_description


def metadata():
    meta = {}
    with open(path.join(cwd, "yandex_cloud_client", "version.py"), "r") as fh:
        exec(fh.read(), meta)

    return meta


def requirements():
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list


metadata = metadata()
readme = readme()
packages = find_packages()
requirements = requirements()


setup(
    name='yandex-cloud-client',
    version=metadata.get('__version__'),
    author=metadata.get('__author__'),
    author_email=metadata.get('__author_email__'),
    license=metadata.get('__license__'),
    description=metadata.get('__description__'),
    long_description=readme,
    long_description_content_type="text/markdown",
    platforms=["osx", "linux"],
    url=metadata.get('__url__'),
    keywords=['yandex cloud client', 'rest api', 'yandex cloud client'],
    classifiers = [
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
    packages=packages,
    install_requires=requirements,
    include_package_data=True,
    python_requires='>=3.7',
    zip_safe=False
)
