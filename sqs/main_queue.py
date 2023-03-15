import boto3
from botocore.exceptions import ClientError

from scrapy.crawler import CrawlerProcess
from imobiliare_scraper.imobiliare_scraper.spiders.imobiliare_spider import ImobiliareSpider

import json
import os

from dotenv import load_dotenv
load_dotenv()


class SQSMainQueue:

    # Get AWS credentials
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    REGION_NAME = os.getenv('REGION_NAME')
    SQS_MAIN_QUEUE_NAME = os.getenv('SQS_MAIN_QUEUE')

    def __init__(self):
        self.session = None
        self.sqs = None
        self.queue = None
        self.message = None
        self.process = None
        self.urls = None

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
            self.queue = self.sqs.Queue(self.SQS_MAIN_QUEUE_NAME)

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
                self.urls = json.loads(self.message[0].body)['urls']

                self.process = CrawlerProcess()
                self.process.crawl(
                    crawler_or_spidercls=ImobiliareSpider,
                    urls=self.urls
                )
                self.process.start()
                self.message[0].delete()
            else:
                print('Nothing on the queue')
        except ClientError as error:
            raise error


def main():
    queue = SQSMainQueue()
    queue.process_message()


if __name__ == '__main__':
    main()
