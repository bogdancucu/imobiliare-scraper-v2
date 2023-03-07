# This script checks SQS Dead Letter Queue every 12 hours for any failed messages.
import boto3

import os

from dotenv import load_dotenv
load_dotenv()

# Get AWS credentials from .env
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')
SQS_DEAD_LETTER_QUEUE = os.getenv('SQS_DEAD_LETTER_QUEUE')

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)

sqs = session.resource('sqs')

queue = sqs.Queue(SQS_DEAD_LETTER_QUEUE)


def main():
    # Retrieve message from SQS Queue
    message = queue.receive_messages(MaxNumberOfMessages=1,
                                     WaitTimeSeconds=2,
                                     VisibilityTimeout=3)

    # Process message
    if message:
        # Todo: process the message
        pass
    else:
        # Todo: nothing to process. log this somewhere
        pass


if __name__ == '__main__':
    main()
