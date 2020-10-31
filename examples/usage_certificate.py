import os
import time
import yaml

from yandex_cloud_client.client import CertificateClient

TOKEN = "YOUR_OAUTH_TOKEN"
client = CertificateClient(oauth_token=TOKEN)


def create_free_cert(folder, name, domains, challenge_type):
    operation = client.createLetsEncryptCertificate(
        folder_id=folder,
        name=name,
        domains=domains,
        challenge_type=challenge_type
    )
    return operation.metadata.certificate_id  # get certificate id from operation metadata


def get_vaildated_certificate(cid):
    cert = client.certificate(cid)
    content = cert.content()

    print('Name:', cert.name)
    print('Status:', cert.status)
    print('Domains:', ','.join(cert.domains) if cert.domains else 'Empty')
    print('Expires:', cert.expires)

    print('\nFullChain:\n', ''.join(content.fullchain))
    print('PrivateKey:\n', content.private_key)


def get_not_vaildated_certificate(cid):
    cert = client.certificate(cid)

    print('Name:', cert.name)
    print('Status:', cert.status)
    print('Domains:', ','.join(cert.domains))

    for challenge in cert.challenges:
        print('\n', challenge.message, sep='')
        print('Status:', challenge.status)
        print('Record Name:', challenge.dns_challenge.name)
        print('Record Type:', challenge.dns_challenge.type)
        print('Record Content:', challenge.dns_challenge.value)


if __name__ == '__main__':
    get_vaildated_certificate("YOUR EXISTING VALID CERTIFICATE")  # if you own validated cert

    new_cert = create_free_cert(
        folder="YOUR_FOLDER_ID",
        name="test",
        domains=[
            "example.com",
            "example.ru"
        ],
        challenge_type="DNS"
    )

    get_not_vaildated_certificate(new_cert)
