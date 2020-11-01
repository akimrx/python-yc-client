#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as fh:
        long_description = fh.read()

    return long_description


def requirements():
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list


packages = find_packages()
requirements = requirements()


setup(
    name='yandex-cloud-client',
    version='1.0.2b',
    author='Akim Faskhutdinov',
    author_email='akimstrong@yandex.ru',
    license='GPLv3',
    description='Unofficial Yandex.Cloud REST API Client',
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/akimrx/python-yc-client",
    keywords='yandex cloud rest api client',
    packages=packages,
    install_requrements=requirements,
    include_package_data=True,
    python_requires='>=3.6',
    zip_safe=False
)
