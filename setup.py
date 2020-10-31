#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


def requirements():
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list


packages = find_packages()
requirements = requirements()


setup(name='python-yc-client',
        version='1.0.2',
        author='Akim Faskhutdinov',
        author_email='akimstrong@yandex.ru',
        license='GPLv3',
        description='Unofficial Yandex.Cloud REST API Client',
        keywords='yandex cloud rest api client',
        packages=packages,
        install_requrements=requirements,
        include_package_data=True,
        zip_safe=False
)
