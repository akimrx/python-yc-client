#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains an object that represents Yandex.Cloud errors."""

class YandexCloudError(Exception):
    pass


class InvalidToken(YandexCloudError):
    pass


class Unauthorized(YandexCloudError):
    pass


class NetworkError(YandexCloudError):
    pass


class BadRequest(YandexCloudError):
    pass


class ResourceNotFound(YandexCloudError):
    pass


class TooManyArguments(YandexCloudError):
    pass


class CertificateError(YandexCloudError):
    pass


class PermissionDenied(YandexCloudError):
    pass


class FeatureNotImplemented(YandexCloudError):
    pass


class ReourceExhausted(YandexCloudError):
    pass


class OperationDeadlineExceeded(YandexCloudError):
    pass


class HTTPError(YandexCloudError):
    pass


class TimedOut(YandexCloudError):
    def __init__(self):
        super().__init__('Timed out')
