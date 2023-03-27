import os

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst

import logging
from cloudwatch import cloudwatch

from dotenv import load_dotenv
load_dotenv()

# Get AWS credentials from .env
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')
S3_BUCKET_PATH = os.getenv('S3_BUCKET_PATH')
LOG_GROUP = os.getenv('LOG_GROUP')
LOG_STREAM_SPIDER = os.getenv('LOG_STREAM_SPIDER')

# CloudWatch logging configuration
logging.basicConfig(
    level=logging.DEBUG,
)
logger = logging.getLogger('imobiliare_spider')
handler = cloudwatch.CloudwatchHandler(
    access_id=AWS_ACCESS_KEY_ID,
    access_key=AWS_SECRET_ACCESS_KEY,
    region=AWS_REGION_NAME,
    log_group=LOG_GROUP,
    log_stream=LOG_STREAM_SPIDER
)
logger.addHandler(hdlr=handler)


class ImobiliareSpider(scrapy.Spider):
    name = 'imobiliare'
    allowed_domains = ['imobiliare.ro']

    custom_settings = {
        'FEEDS': {
            f'{S3_BUCKET_PATH}%(batch_time)s.json': {
                'format': 'json',
                'overwrite': True,
                'indent': 2,
                'encoding': 'utf8'
            }
        },
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'CONCURRENT_REQUESTS': '4',
        'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID,
        'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY,
        'AWS_REGION_NAME': AWS_REGION_NAME
    }

    def __init__(self, urls: list, *args, **kwargs):
        super(ImobiliareSpider, self).__init__(*args, **kwargs)
        self.urls = urls

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.log_errors,
                cb_kwargs=dict(url=url)
            )

    def parse(self, response, **kwargs):
        scraped_response = dict()
        item = ItemLoader(item=scraped_response, response=response)

        item.default_output_processor = TakeFirst()

        try:
            item.add_css(field_name='uid', css='span.id::text')
            for spec_name, spec_value in list(zip(
                response.css('li.list-group-item.specificatii-oferta__lista--item::text').getall(),
                response.css('li.list-group-item.specificatii-oferta__lista--item span::text').getall(),
                strict=True
            )):
                item.add_value(field_name=spec_name, value=spec_value)
        except Exception as error:
            logger.error(error)
            raise error
        else:
            return item.load_item()

    def log_errors(self, failure):
        logger.error(f'{repr(failure)}. url: {failure.request.cb_kwargs["url"]}')
