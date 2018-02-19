from os import listdir, path

import boto3
from botocore.exceptions import ClientError
from toolz.functoolz import excepts
from wedding.general.functional import option
from wedding.general.store import Store
from wedding.model import Party


def _is_image(filename: str) -> bool:
    return any(filename.endswith(extension) for extension in [
        '.png',
        '.jpg',
        '.jpeg',
        '.gif'
    ])


def upload_envelopes(envelope_dir: str,
                     resource_bucket: str,
                     envelope_prefix: str,
                     parties: Store[str, Party]) -> None:
    client = boto3.client('s3')

    for envelope in listdir(envelope_dir):
        envelope_file = path.join(envelope_dir, envelope)

        if path.isfile(envelope_file) and _is_image(envelope_file):
            maybe_party = excepts(
                ClientError,
                parties.get
            )(path.splitext(path.basename(envelope_file))[0])

            envelope_key = envelope_prefix + ('/' if not envelope_prefix.endswith('/') else '') + envelope

            client.upload_file(
                envelope_file,
                resource_bucket,
                envelope_key
            )

            option.fmap(
                lambda party:
                client.put_object_tagging(
                    Bucket = resource_bucket,
                    Key    = envelope_key   ,
                    Tagging = {
                        'TagSet': [
                            {
                                'Key': 'party',
                                'Value': party.title
                            }
                        ]
                    }
                )
            )(maybe_party)
