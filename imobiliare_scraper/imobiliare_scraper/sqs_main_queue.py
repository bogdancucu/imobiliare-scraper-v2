import boto3

from scrapy.crawler import CrawlerProcess
from spiders.imobiliare_spider import ImobiliareSpider

import json
import os

from dotenv import load_dotenv
load_dotenv()

# Get AWS credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')
SQS_MAIN_QUEUE = os.getenv('SQS_MAIN_QUEUE')

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)

sqs = session.resource('sqs')

queue = sqs.Queue(SQS_MAIN_QUEUE)


def main():
    # Retrieve message from SQS Queue
    message = queue.receive_messages(MaxNumberOfMessages=1,
                                     WaitTimeSeconds=2,
                                     VisibilityTimeout=3)

    # Process message
    if message:
        body_dict = json.loads(message[0].body)
        urls = body_dict['urls']

        # Crawl
        process = CrawlerProcess()
        process.crawl(
            crawler_or_spidercls=ImobiliareSpider,
            urls=urls
        )
        process.start(stop_after_crawl=True)
        message[0].delete()

    else:
        print('Nothing on the queue.')


if __name__ == '__main__':
    main()
