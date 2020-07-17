#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains ServiceAccount, ServiceAccountAuth class."""

import jwt
import time

from yandex_cloud_client.base import YandexCloudObject
from yandex_cloud_client.utils.endpoints import IAM_URL


class ServiceAccount(YandexCloudObject):
    def __init__(self):
        pass


class ServiceAccountAuth:
    """This class represents auth method for service account.

    Args:
      :service_account_key: dict (decoded from key.json)

    Methods:
      generate_jwt()

    """

    def __init__(self, service_account_key: dict):
        self._sa_key = service_account_key
        self._validate_sa_format()

    @property
    def id(self):
        """Validating service account key."""
        _id = self._sa_key.get('id')
        if _id is None:
            raise KeyError(f'Invalid service account key, missing: id')
        return _id

    @property
    def service_account_id(self):
        """Validating service account id."""
        _service_account_id = self._sa_key.get('service_account_id')
        if _service_account_id is None:
            raise KeyError(f'Invalid service account key, missing: service_account_id')
        return _service_account_id

    @property
    def key_algorithm(self):
        return self._sa_key.get('key_algorithm')

    @property
    def private_key(self):
        """Validating service account private key."""
        prefix_start = '-----BEGIN PRIVATE KEY-----'
        _private_key = self._sa_key.get('private_key')

        if _private_key is None:
            raise KeyError(f'Invalid service account key, missing: private_key')

        elif not _private_key.startswith(prefix_start):
            raise TypeError(f'Invalid private key format, required format: SHA-256')

        return _private_key

    @property
    def public_key(self):
        return self._sa_key.get('public_key')

    def _validate_sa_format(self):
        """Validating service account key format."""
        if not isinstance(self._sa_key, dict):
            message = f'Invalid service account key. Required format: dict, ' + \
                      f'but received: {type(self._sa_key)}'
            raise TypeError(message)

    def generate_jwt(self):
        """This method prepare data for request IAM token."""
        now = time.time()
        payload = {
            "iss": self.service_account_id,
            "aud": IAM_URL + "/iam/v1/tokens",
            "iat": now,
            "exp": now + 360,
        }

        headers = {
            "typ": "JWT",
            "alg": "PS256",
            "kid": self.id,
        }

        return jwt.encode(payload, self.private_key, algorithm='PS256', headers=headers)
