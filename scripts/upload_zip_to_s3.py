"""
Upload a set of documents from a zip file to the local S3 bucket.

Example of usage:
> python upload_zip_to_s3.py 'test_zip.zip' 'unzip_folder' --bucket mojap-rd --prefix test_upload/docs --no-local
"""
import argparse
import os
import zipfile

from glob import glob
from pathlib import Path

import boto3

parser = argparse.ArgumentParser(prog="Document uploader")
parser.add_argument("zipfile", help="Path to zip file")
parser.add_argument("destdir", help="Destination directory to unzip to")
parser.add_argument("--bucket", help="S3 bucket to upload files to", default="mojap-rd")
parser.add_argument("--prefix", help="Prefix to put in front of S3 keys for each uploaded file", default="gdd_capability/gdd_capability_pay")
parser.add_argument('--local', action=argparse.BooleanOptionalAction, dest='local', help="Use --local for localstack, or --no-local for an s3 bucket on the MoJ Analytical Platform", default=False)

args = parser.parse_args()

destdir_path = Path(args.destdir)

os.makedirs(destdir_path, exist_ok=True)

# unzip
with zipfile.ZipFile(args.zipfile, "r") as zip_file:
    zip_file.extractall(destdir_path)

# get list of files
files_to_upload = glob(f"{destdir_path / '**/*'}")

# upload files to s3 bucket; NB in localstack, we can just use
# "localstack" for auth
if args.local:
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="localstack",
        aws_secret_access_key="localstack"
    )
else:
    s3 = boto3.client("s3")

prefix = args.prefix.strip("/")
for f in files_to_upload:
    if not os.path.isfile(f):
        continue

    key = f"{prefix}/{os.path.basename(f)}"
    print(f"Uploading {key}")
    s3.upload_file(f, args.bucket, key)
