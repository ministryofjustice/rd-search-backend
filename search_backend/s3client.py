import logging
import os
from io import BytesIO
from typing import Optional

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError


def _get_error_message(ex: Exception) -> str:
    if isinstance(ex, ClientError):
        return f"ERROR: {ex}"
    if isinstance(ex, EndpointConnectionError):
        return "ERROR: unable to connect to S3 endpoint"
    return "ERROR: unknown error occurred"


class S3Client:

    def __init__(self, s3bucket: str, prefix: str, client: boto3.client):
        self.bucket = s3bucket
        self.prefix = prefix.strip("/")
        self.client = client
        boto3.set_stream_logger("", logging.INFO)

    # returns None (no error), or error message
    def upload(
        self, bytes_to_upload: bytes, filename: str
    ) -> Optional[str]:
        try:
            self.client.upload_fileobj(
                BytesIO(bytes_to_upload),
                self.bucket,
                f"{self.prefix}/{os.path.basename(filename)}",
            )

            return None
        except Exception as ex:
            return _get_error_message(ex)

    # key: key for the object, excluding the prefix
    # prepend_prefix: if True, prefix is prepended to the key before doing the get
    # returns (data, error); data is None if error occurred; error is None if retrieval was successful
    def get_object(self, key: str, prepend_prefix=True) -> tuple:
        if prepend_prefix:
            key = f"{self.prefix}/{key}"

        try:
            data = self.client.get_object(Bucket=self.bucket, Key=key)
            return data, None
        except Exception as ex:
            return None, _get_error_message(ex)

    # Get a list of objects in the bucket with given prefix.
    #
    # returns (objects: list, error: str); if an error occurred, error is not None
    # and list is empty
    def list(self) -> tuple:
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket, Prefix=f"{self.prefix}/"
            )

            objs = []
            if "Contents" in response:
                objs = response["Contents"]

            return objs, None
        except Exception as ex:
            return [], _get_error_message(ex)
