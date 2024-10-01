import boto3


# env: dict derived from get_config()
def get_aws_session(env: dict, aws_region: str) -> boto3.Session:
    aws_web_identity_token_file = env.get("AWS_WEB_IDENTITY_TOKEN_FILE")
    aws_role_arn = env.get("AWS_ROLE_ARN")

    if aws_web_identity_token_file is not None and aws_role_arn is not None:
        with open(env["AWS_WEB_IDENTITY_TOKEN_FILE"], 'r') as content_file:
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
