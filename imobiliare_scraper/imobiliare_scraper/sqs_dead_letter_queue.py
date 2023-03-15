import boto3
from botocore.exceptions import ClientError

import os

from dotenv import load_dotenv
load_dotenv()


class SQSDeadLetterQueue:

    # Get AWS credentials
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    REGION_NAME = os.getenv('REGION_NAME')
    SQS_DEAD_LETTER_QUEUE = os.getenv('SQS_DEAD_LETTER_QUEUE')

    def __init__(self):
        self.session = None
        self.sqs = None
        self.queue = None
        self.message = None

    def _create_aws_session(self):
        return boto3.Session(
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region_name=self.REGION_NAME
        )

    def _get_message(self):
        try:
            self.session = self._create_aws_session()
            self.sqs = self.session.resource('sqs')
            self.queue = self.sqs.Queue(self.SQS_DEAD_LETTER_QUEUE)

            return self.queue.receive_messages(
                MaxNumberOfMessages=1,
                WaitTimeSeconds=2,
                VisibilityTimeout=3
            )
        except ClientError as error:
            raise error

    def process_message(self):
        self.message = self._get_message()

        try:
            if self.message:
                pass
                # TODO: process message
            else:
                pass
                # TODO: update logfile
        except ClientError as error:
            raise error


def main():
    queue = SQSDeadLetterQueue()
    queue.process_message()


if __name__ == '__main__':
    main()
