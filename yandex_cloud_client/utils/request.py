#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Request wrapper."""

import re
import json
import logging
import requests

from enum import Enum

from yandex_cloud_client.constants import DEFAULT_TIMEOUT
from yandex_cloud_client.utils.response import Response
from yandex_cloud_client.utils.decorators import retry

from yandex_cloud_client.error import (Unauthorized, BadRequest, PermissionDenied, NetworkError,
                                       YandexCloudError, TimedOut, ResourceNotFound,
                                       FeatureNotImplemented, ReourceExhausted, HTTPError)


logger = logging.getLogger('requests.packages.urllib3')

HEADERS = {
    'content-type': 'application/json'
}


class Request:
    """Base HTTP request wrapper for Yandex.Cloud API.

    If you need proxy, use:
    proxy_url='socks5://user:password@host:port'

    """

    def __init__(self,
                 client=None,
                 headers=None,
                 proxy_url=None,
                 timeout=5):

        self.headers = headers or HEADERS.copy()
        self.client = self.set_and_return_client(client)
        self.proxies = {'http': proxy_url, 'https': proxy_url} if proxy_url else None
        self.timeout = int(timeout) if timeout is not None else DEFAULT_TIMEOUT

    def set_authorization(self, token):
        self.headers.update({'Authorization': f'Bearer {token}'})

    def set_and_return_client(self, client):
        self.client = client

        if self.client and self.client.token:
            self.set_authorization(self.client.token)

        return self.client

    @staticmethod
    def _convert_camel_to_snake(text):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def _object_hook(obj: dict):
        cleaned_object = {}
        for key, value in obj.items():
            key = Request._convert_camel_to_snake(key.replace('-', '_'))

            if len(key) and key[0].isdigit():
                key = '_' + key

            cleaned_object.update({key: value})
        return cleaned_object

    def _parse(self, json_data: bytes):
        try:
            decoded_s = json_data.decode('utf-8')
            data = json.loads(decoded_s, object_hook=Request._object_hook)
        except UnicodeDecodeError:
            logger.debug('Logging raw invalid UTF-8 response:\n%r', json_data)
            raise YandexCloudError('Server response could not be decoded using UTF-8')
        except (AttributeError, ValueError):
            raise YandexCloudError('Invalid server response', json_data)

        if data.get('result') is None:
            data = {
                'result': data,
                'error': data.get('error') or RpcError(data.get('code', 2)),
                'error_description': data.get('error_description') or data.get('message')
            }

        return Response.de_json(data, self.client)

    @retry((NetworkError, TimedOut))
    def _request_wrapper(self, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        try:
            resp = requests.request(*args, **kwargs)
        except requests.Timeout:
            raise TimedOut()
        except requests.RequestException as e:
            raise NetworkError(e)

        if 200 <= resp.status_code <= 299:
            return resp

        logger.debug(resp.content)
        parse = self._parse(resp.content)
        message = parse.error or 'Unknown HTTPError'

        if resp.status_code == 401:
            raise Unauthorized(message)
        elif resp.status_code == 400:
            raise BadRequest(message)
        elif resp.status_code == 403:
            raise PermissionDenied(message)
        elif resp.status_code == 404:
            raise ResourceNotFound(message)
        elif resp.status_code in (409, 413):
            raise HTTPError(f'HTTP {resp.status_code} – {message}')
        elif resp.status_code == 429:
            raise ReourceExhausted(message)

        elif resp.status_code == 510:
            raise FeatureNotImplemented(message)
        else:
            raise HTTPError(f'{resp.status_code} – {message}')

    def get(self, url, params=None, *args, **kwargs):
        result = self._request_wrapper('GET', url, params=params, headers=self.headers,
            proxies=self.proxies, timeout=self.timeout, *args, **kwargs)

        return self._parse(result.content).result

    def post(self, url, data=None, json=None, *args, **kwargs):
        result = self._request_wrapper('POST', url, headers=self.headers, proxies=self.proxies,
            data=data, json=json, timeout=self.timeout, *args, **kwargs)

        return self._parse(result.content).result

    def put(self, url, data=None, json=None, *args, **kwargs):
        result = self._request_wrapper('PUT', url, headers=self.headers, proxies=self.proxies,
            data=data, json=json, timeout=self.timeout, *args, **kwargs)

        return self._parse(result.content).result

    def patch(self, url, data=None, json=None, *args, **kwargs):
        result = self._request_wrapper('PATCH', url, headers=self.headers, proxies=self.proxies,
            data=data, json=json, timeout=self.timeout, *args, **kwargs)

        return self._parse(result.content).result

    def delete(self, url, *args, **kwargs):
        result = self._request_wrapper('DELETE', url, headers=self.headers, proxies=self.proxies,
            timeout=self.timeout, *args, **kwargs)

        return self._parse(result.content).result


class RpcError(Enum):
    """This class convert grpc digit codes to messages."""

    CANCELLED = 1
    UNKNOWN = 2
    INVALID_ARGUMENT = 3
    DEADLINE_EXCEEDED = 4
    NOT_FOUND = 5
    ALREADY_EXISTS = 6
    PERMISSION_DENIED = 7
    RESOURCE_EXHAUSTED = 8
    FAILED_PRECONDITION = 9
    ABORTED = 10
    OUT_OF_RANGE = 11
    NOT_IMPLEMENTED = 12
    INTERNAL = 13
    UNAVAILABLE = 14
    DATA_LOSS = 15
    UNAUTHENTICATED = 16
