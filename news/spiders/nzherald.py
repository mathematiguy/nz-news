# -*- coding: utf-8 -*-
import re
import logging
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

def remove_tags(s):
    tags_match = re.compile('<[^>]+>')
    s = s.replace("<br>", "\n")
    return tags_match.sub('', s)


def get_byline(response):
    byline_tag = response.xpath('//div/div[contains(@class, "author-name")]')
    if byline_tag:
        byline = [remove_tags(s) for s in byline_tag.extract()]
        return byline


class NzheraldSpider(CrawlSpider):
    name = 'nzherald'
    allowed_domains = ['www.nzherald.co.nz']
    start_urls = ['https://www.nzherald.co.nz/']

    object_ids = []

    rules = (
        # Extract links containing an objectid and parse them with the spider's method parse_article
        Rule(
            LinkExtractor(
                unique=True,
                allow=('objectid=\d+', ),
                deny=("objectid={}".format(s) for s in object_ids)
                ),
            callback='parse_article',
            follow=True
        ),
    )

    def parse_article(self, response):

        # append object_id to cache list
        object_id = re.search("objectid=(\d+)", response.url)
        if object_id:
            object_id = object_id.group(1)
        else:
            logging.debug("Filtering request to parse: {}".format(response.url))
            return

        byline = get_byline(response)
        date = ' '.join(response.xpath('//div[contains(@class, "publish")]/text()').extract()).strip()
        headline = [remove_tags(p) for p in response.xpath('//h1').extract()]
        sponsor = [remove_tags(s) for s in response.xpath('//div[contains(@class, "sponsored-text")]').extract()]
        subheader = response.xpath('//meta[@itemprop="description"]/@content').extract()
        syndicator_name = response.xpath('//div[contains(@class, "syndicator-name")]/span/text()').extract()
        paragraphs = [remove_tags(p) for p in response.xpath('//div[@id="article-content"]/p/text()').extract()]

        yield {
            'url': response.url,
            'byline': byline,
            'date': date,
            'headline': headline,
            'sponsor': sponsor,
            'subheader': subheader,
            'syndicator_name': syndicator_name,
            'paragraphs': paragraphs
        }
