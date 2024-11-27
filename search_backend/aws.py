import boto3


def get_aws_session(env: dict, aws_region: str) -> boto3.Session:
    """
    Get an AWS session, either using a token file (when running on the Cloud Platform)
    or access and secret access keys (locally).
    The intention is that this gives a simple way to access AWS credentials.

    Note that the token expires on the Cloud Platform, so the session should be
    regenerated every time a call is made to AWS.

    :param env: dict containing either:
        AWS_WEB_IDENTITY_TOKEN_FILE and AWS_ROLE_ARN
      OR
        AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    :param aws_region: AWS region string, e.g. "eu-west-1"
    """
    aws_web_identity_token_file = env.get("AWS_WEB_IDENTITY_TOKEN_FILE")
    aws_role_arn = env.get("AWS_ROLE_ARN")

    if aws_web_identity_token_file is not None and aws_role_arn is not None:
        with open(env["AWS_WEB_IDENTITY_TOKEN_FILE"], "r") as content_file:
            web_identity_token = content_file.read()

            role = boto3.client("sts").assume_role_with_web_identity(
                RoleArn=aws_role_arn,
                RoleSessionName="assume-role",
                WebIdentityToken=web_identity_token,
            )

            credentials = role["Credentials"]

            aws_access_key_id = credentials["AccessKeyId"]
            aws_secret_access_key = credentials["SecretAccessKey"]
            aws_session_token = credentials["SessionToken"]
    else:
        aws_access_key_id = env["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = env["AWS_SECRET_ACCESS_KEY"]
        aws_session_token = None

    return boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=aws_region,
    )
