#!/usr/bin/env python3
"""This module contains Certificate, CertificateContent, CertificateRequestSpec, Challenges, DnsChallenges and HttpChallenges classes."""

import logging

from yandex_cloud_client.base import YandexCloudObject
from yandex_cloud_client.utils.helpers import universal_obj_hook, string_to_datetime

logger = logging.getLogger(__name__)


class Certificate(YandexCloudObject):
    """This class representing a managed certificate.

    Attributes:
      :id: str
      :folder_id: str
      :created_at: datetime
    """

    def __init__(self,
                 id=None,
                 folder_id=None,
                 created_at=None,
                 name=None,
                 description=None,
                 labels=None,
                 type=None,
                 domains=None,
                 status=None,
                 subject=None,
                 serial=None,
                 updated_at=None,
                 issued_at=None,
                 not_after=None,
                 not_before=None,
                 challenges=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        # Required
        self.id = id

        # Optional
        self.folder_id = folder_id
        self.created_at = string_to_datetime(created_at) if created_at is not None else created_at
        self.name = name
        self.description = description
        self.labels = labels
        self.type = type
        self.domains = domains
        self.status = status
        self.subject = subject
        self.serial = serial
        self.updated_at = string_to_datetime(updated_at) if updated_at is not None else updated_at
        self.issued_at = string_to_datetime(issued_at) if issued_at is not None else issued_at
        self.not_after = string_to_datetime(not_after) if not_after is not None else not_after
        self.not_before = string_to_datetime(not_before) if not_before is not None else not_before
        self.challenges = challenges

        self.client = client
        self._id_attrs = (self.id,)

    @property
    def expires(self):
        return self.not_after

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Certificate, cls).de_json(data, client)
        data['challenges'] = Challenges.de_list(universal_obj_hook(data.get('challenges')), client)
        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        certificates = list()
        for certificate in data:
            certificates.append(cls.de_json(certificate, client))

        return certificates

    def content(self, *args, **kwargs):
        """Shortcut for client.certificate_content()."""
        return self.client.certificate_content(self.id, *args, **kwargs)

    def delete(self, run_async_await=False, await_complete=True, *args, **kwargs):
        """Shortcut for client.delete_certificate()."""
        return self.client.delete_certificate(self.id, await_complete, run_async_await, *args, **kwargs)


class Challenges(YandexCloudObject):

    def __init__(self,
                 domain=None,
                 type=None,
                 created_at=None,
                 updated_at=None,
                 status=None,
                 message=None,
                 error=None,
                 dns_challenge=None,
                 http_challenge=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.domain = domain
        self.type = type
        self.created_at = string_to_datetime(created_at) if created_at is not None else created_at
        self.updated_at = string_to_datetime(updated_at) if updated_at is not None else updated_at
        self.status = status
        self.message = message
        self.error = error
        self.dns_challenge = dns_challenge
        self.http_challenge = http_challenge

        self.client = client

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(Challenges, cls).de_json(data, client)

        data['dns_challenge'] = DnsChallenges.de_json(universal_obj_hook(data.get('dns_challenge')), client)
        data['http_challenge'] = HttpChallenges.de_json(universal_obj_hook(data.get('http_challenge')), client)

        return cls(client=client, **data)

    @classmethod
    def de_list(cls, data: list, client):
        if not data:
            return []

        challenges = list()
        for challenge in data:
            challenges.append(cls.de_json(challenge, client))

        return challenges


class DnsChallenges(YandexCloudObject):

    def __init__(self,
                 name=None,
                 type=None,
                 value=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.name = name
        self.type = type
        self.value = value

        self.client = client

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(DnsChallenges, cls).de_json(data, client)
        return cls(client=client, **data)


class HttpChallenges(YandexCloudObject):

    def __init__(self,
                 url=None,
                 content=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.url = url
        self.content = content

        self.client = client

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(HttpChallenges, cls).de_json(data, client)
        return cls(client=client, **data)


class CertificateContent(YandexCloudObject):

    def __init__(self,
                 id=None,
                 certificate_id=None,
                 certificate_chain=None,
                 private_key=None,
                 client=None,
                 **kwargs):

        super().handle_unknown_kwargs(self, **kwargs)

        self.id = certificate_id
        self.certificate_id = certificate_id
        self.certificate_chain = certificate_chain
        self.private_key = private_key

        self.client = client
        self._id_attrs = (self.id,)

    @property
    def chain(self):
        return self.certificate_chain

    @property
    def fullchain(self):
        return self.certificate_chain

    @classmethod
    def de_json(cls, data: dict, client):
        if not data:
            return None

        data = super(CertificateContent, cls).de_json(data, client)
        return cls(client=client, **data)


class CertificateRequestSpec(YandexCloudObject):

    def __init__(self,
                 folder_id=None,
                 name=None,
                 description=None,
                 labels=None,
                 domains=None,
                 challenge_type=None,
                 client=None,
                 **kwargs):

        # Required
        self.folderId = folder_id

        # Optional
        self.name = name
        self.description = description
        self.labels = labels
        self.domains = domains
        self.challengeType = challenge_type

        self.client = client

    @classmethod
    def prepare(cls, data: dict, client):
        """Deserializing and preparing for a request."""
        if not data:
            return None

        data = super(CertificateRequestSpec, cls).de_json(data, client)
        result = cls(client=client, **data).to_dict()

        # cleaning None-type keys
        cleaner = lambda x: dict((k, v) for (k, v) in x.items() if v is not None)

        return cleaner(result)
