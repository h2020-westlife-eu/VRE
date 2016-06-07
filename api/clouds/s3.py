# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

import tempfile
import traceback
import uuid

import boto3
import botocore.exceptions


def get_s3_bucket(s3_provider):
    try:
        s3 = boto3.resource(
            's3',
            aws_access_key_id=s3_provider.access_key_id,
            aws_secret_access_key=s3_provider.secret_access_key
        )
        try:
            bucket = s3.create_bucket(
                Bucket=s3_provider.bucket_name,
                CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}
            )
        except:
            bucket = s3.Bucket(s3_provider.bucket_name)
            exists = True
            try:
                s3.meta.client.head_bucket(Bucket=s3_provider.bucket_name)
            except botocore.exceptions.ClientError as e:
                # If a client error is thrown, then check if it was a 404 error.
                # If it was a 404 error, then the bucket does not exist
                error_code = int(e.response['Error']['Code'])
                if error_code == 404:
                    exists = False

                # We raise anyway, whatever the error
                raise
    except:
        print(traceback.format_exc())
        return None
    else:
        return s3


def check_s3_credentials(s3_provider):
    s3 = get_s3_bucket(s3_provider)
    if s3 is None:
        raise RuntimeError('Invalid S3 credentials for %d' % (s3_provider.pk,))


def upload_file_to_s3(datafile, s3_provider, tempfile_path):
    s3 = get_s3_bucket(s3_provider)

    if s3 is None:
        raise RuntimeError('Could not get S3 connection')

    storage_key = str(uuid.uuid4())
    s3.Object(s3_provider.bucket_name, storage_key).put(Body=open(tempfile_path, 'rb'))

    return storage_key


def retrieve_file_from_s3(datafile, s3_provider):
    s3 = get_s3_bucket(s3_provider)

    if s3 is None:
        print('Could not get S3 connection')
        return None

    else:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                tmpfilename = tmpfile.name

            s3.Bucket(s3_provider.bucket_name).download_file(datafile.storage_key, tmpfilename)
            return tmpfilename

        except:
            print('Download failed: %s' % traceback.format_exc())
            return None


def delete_file_from_s3(s3_provider, storage_key):
    s3 = get_s3_bucket(s3_provider)

    if s3 is None:
        print('Could not get S3 connection')
        return False

    else:
        try:
            s3.Object(s3_provider.bucket_name, storage_key).delete()
            return True
        except:
            print('Delete failed: %s' % traceback.format_exc())
            return False
