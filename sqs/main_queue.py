import boto3
from botocore.exceptions import ClientError

from scrapy.crawler import CrawlerProcess
from imobiliare_scraper.imobiliare_scraper.spiders.imobiliare_spider import ImobiliareSpider

import logging
from cloudwatch import cloudwatch

import json
import os

from dotenv import load_dotenv
load_dotenv()

# get AWS credentials from .env file
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')
SQS_MAIN_QUEUE = os.getenv('SQS_MAIN_QUEUE')
LOG_GROUP = os.getenv('LOG_GROUP')
LOG_STREAM = os.getenv('LOG_STREAM_SQS')

# Configure logger
logging.basicConfig(
    level=logging.DEBUG,
)
logger = logging.getLogger('sqs_main_queue')
handler = cloudwatch.CloudwatchHandler(
    access_id=AWS_ACCESS_KEY_ID,
    access_key=AWS_SECRET_ACCESS_KEY,
    region=REGION_NAME,
    log_group=LOG_GROUP,
    log_stream=LOG_STREAM
)
logger.addHandler(hdlr=handler)


class SQSMainQueue:

    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, sqs_main_queue):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.sqs_main_queue = sqs_main_queue
        self.queue = None
        self.message = None
        self.process = None
        self.urls = None

    def _create_aws_queue_resource(self):
        return boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        ).resource('sqs').Queue(self.sqs_main_queue)

    def _get_message(self):
        try:
            logger.info('Creating AWS resources')
            self.queue = self._create_aws_queue_resource()
            logger.info('Pooling for messages')
            return self.queue.receive_messages(
                MaxNumberOfMessages=1,
                WaitTimeSeconds=2,
                VisibilityTimeout=3
            )
        except ClientError as error:
            logger.error(f'{error}')
            raise error

    def process_message(self):
        self.message = self._get_message()

        try:
            if self.message:
                logger.info('Message on queue. Retrieving for further processing')
                self.urls = json.loads(self.message[0].body)['urls']

                logger.info(f'Starting the crawl for {len(self.urls)} urls: {self.urls}')
                self.process = CrawlerProcess()
                self.process.crawl(
                    crawler_or_spidercls=ImobiliareSpider,
                    urls=self.urls
                )
                self.process.start()
                self.message[0].delete()
            else:
                logger.info('Nothing on the queue')
        except ClientError as error:
            logger.error(f'{error}')
            raise error
        else:
            logger.info('Crawl finished')


def main():
    queue = SQSMainQueue(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION_NAME,
        sqs_main_queue=SQS_MAIN_QUEUE
    )
    queue.process_message()


if __name__ == '__main__':
    main()
