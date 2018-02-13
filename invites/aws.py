import boto3
from os import listdir
from os.path import isfile, join


def upload_envelopes(envelope_dir: str,
                     envelope_bucket: str) -> None:
    bucket = boto3.resource('s3').Bucket(envelope_bucket)
    for envelope in listdir(envelope_dir):
        envelope_file = join(envelope_dir, envelope)
        if isfile(envelope_file):
            bucket.upload_file(
                envelope_file,
                envelope
            )
