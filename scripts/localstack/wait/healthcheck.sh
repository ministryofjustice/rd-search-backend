#!/usr/bin/env bash
buckets=$(awslocal s3 ls)
echo $buckets | grep $S3_BUCKET || exit 1
