#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Response class."""

from yandex_cloud_client.base import YandexCloudObject


class Response(YandexCloudObject):
    """This object represents a response from Yandex.Cloud API."""

    def __init__(self,
                 data: dict,
                 result=None,
                 error=None,
                 error_description=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.data = data
        self._result = result
        self._error = error
        self.error_description = error_description

        self.client = client

    @property
    def error(self) -> str:
        return f'{self._error}: {self.error_description if self.error_description else ""}'

    @property
    def result(self) -> dict:
        return self.data if self._result is None else self._result

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Response, cls).de_json(data, client)
        data['data'] = data.copy()
        return cls(client=client, **data)
