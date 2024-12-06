import unittest
import boto3
from datetime import datetime
from mockito import mock, when
from search_backend.aws import get_aws_session


class TestAWSSession(unittest.TestCase):

    def test_get_session_with_local_keys(self):
        """
        Test assuming we're running locally and have access and secret access keys defined.
        """
        
        config = {
            "AWS_WEB_IDENTITY_TOKEN_FILE": None,
            "AWS_ROLE_ARN": None,
            "AWS_ACCESS_KEY_ID": "DUMMY_KEY_ID_1",
            "AWS_SECRET_ACCESS_KEY": "DUMMY_SECRET_KEY_1",
            "AWS_REGION": None,
        }

        aws_session = get_aws_session(config, config.get("AWS_REGION"))
        credentials = aws_session.get_credentials()

        self.assertEqual(credentials.access_key, "DUMMY_KEY_ID_1")
        self.assertEqual(credentials.secret_key, "DUMMY_SECRET_KEY_1")
        self.assertEqual(credentials.token, None)

    def test_get_session_with_token_file(self):
        """
        Test assuming we're running (e.g.) on the Cloud Platform and have a token file.
        """

        config = {
            # config for get_aws_session
            "AWS_WEB_IDENTITY_TOKEN_FILE": "tests/.dummy_token",
            "AWS_ROLE_ARN": "01234567890123456789",
            "AWS_ACCESS_KEY_ID": "DUMMY_KEY_ID_2",
            "AWS_SECRET_ACCESS_KEY": "DUMMY_SECRET_KEY_2",
            "AWS_REGION": "DUMMY_REGION",
        }

        mock_role = {
            'Credentials': {
                'AccessKeyId': config.get("AWS_ACCESS_KEY_ID"),
                'SecretAccessKey': config.get("AWS_SECRET_ACCESS_KEY"),
                'SessionToken': "00000000000000000000",
                'Expiration': datetime(2015, 1, 1)
            },
        }

        sts_client_mock = mock()

        when(boto3).client("sts").thenReturn(sts_client_mock)
        when(sts_client_mock).assume_role_with_web_identity(...).thenReturn(mock_role)

        aws_session = get_aws_session(config, config.get("AWS_REGION"))
        credentials = aws_session.get_credentials()

        self.assertEqual(credentials.access_key, "DUMMY_KEY_ID_2")
        self.assertEqual(credentials.secret_key, "DUMMY_SECRET_KEY_2")
        self.assertEqual(credentials.token, "00000000000000000000")
