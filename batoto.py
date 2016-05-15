import os
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from w3lib.url import add_or_replace_parameter, url_query_parameter


class BatotoImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        yield scrapy.Request(item['image_url'], meta={'item': item})

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        url = request.url
        ext = os.path.splitext(url)[1]
        return '{title}/{chapter}/{page}{extension}'.format(extension=ext, **item)


class BatotoSpider(scrapy.Spider):
    name = 'batoto'
    reader_url = 'http://bato.to/areader?id={id}&p={page}'

    def __init__(self, *args, **kwargs):
        super(BatotoSpider, self).__init__(*args, **kwargs)
        self.start_urls = [self.reader_url.format(id=self.id, page=1)]

    @classmethod
    def update_settings(cls, settings):
        super(BatotoSpider, cls).update_settings(settings)
        pipeline_name = BatotoImagesPipeline.__module__
        pipeline_name += '.' + BatotoImagesPipeline.__name__
        settings['ITEM_PIPELINES'][pipeline_name] = 1

    def make_requests_from_url(self, url):
        return scrapy.Request(
            url,
            headers={
                'Referer': 'http://bato.to/reader',
            },
        )

    def parse(self, response):
        for chapter in response.css(
            'select[name=chapter_select] ::attr(value)'
        ).re('#([a-f0-9]+)'):
            yield scrapy.Request(
                self.reader_url.format(id=chapter, page=1),
                callback=self.parse_chapter,
                headers={
                    'Referer': 'http://bato.to/reader',
                },
            )

        for req in self.parse_chapter(response):
            yield req

    def parse_chapter(self, response):
        for page in response.css('select[name=page_select] ::attr(value)').re('\d+'):
            yield scrapy.Request(
                add_or_replace_parameter(response.url, 'p', page),
                callback=self.parse_page,
                headers={
                    'Referer': 'http://bato.to/reader',
                },
            )

        for item in self.parse_page(response):
            yield item

    def parse_page(self, response):
        chapter_id = url_query_parameter(response.url, 'id')
        page = url_query_parameter(response.url, 'p')
        main_image = response.css('#comic_page')
        yield {
            'image_url': main_image.xpath('@src').extract_first(),
            'image_name': main_image.xpath('@alt').extract_first(),
            'page': page,
            'chapter': response.css(
                '[name=chapter_select] [selected]::text'
            ).extract_first(),
            'chapter_id': chapter_id,
            'url': 'http://bato.to/reader#{}_{}'.format(chapter_id, page),
            'title': response.css('a[href*=comics]::text').extract_first(),
        }
