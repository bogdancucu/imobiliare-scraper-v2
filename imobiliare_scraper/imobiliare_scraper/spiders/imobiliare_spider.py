import os

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst

from dotenv import load_dotenv
load_dotenv()

# Get AWS credentials from .env
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')
S3_BUCKET_PATH = os.getenv('S3_BUCKET_PATH')


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
        self.scraped_response = list()

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        scraped_response = dict()
        item = ItemLoader(item=scraped_response, response=response)

        item.default_output_processor = TakeFirst()

        item.add_css(field_name='uid', css='span.id::text')

        for spec_name, spec_value in list(zip(
            response.css('li.list-group-item.specificatii-oferta__lista--item::text').getall(),
            response.css('li.list-group-item.specificatii-oferta__lista--item span::text').getall(),
            strict=True
        )):
            item.add_value(field_name=spec_name, value=spec_value)

        return item.load_item()
