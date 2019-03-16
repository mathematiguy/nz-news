# -*- coding: utf-8 -*-
import re
import logging
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

def remove_tags(s):
    tags_match = re.compile('<[^>]+>')
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

    with open("nzherald_ids.txt", "w") as f:
        object_ids = f.read().strip().split("\n")

    rules = (
        # Follow all links (in allowed domains)
        Rule(LinkExtractor()),

        # Extract links containing an objectid and parse them with the spider's method parse_article
        Rule(LinkExtractor(
            allow=('objectid=\d+', ),
            deny=("|".join("object_id=%s" % s for s in object_ids),)),

        callback='parse_article'),
    )

    def parse_article(self, response):

        date = response.xpath('//div[contains(@class, "publish")]/text()').extract()
        date = ' '.join(date).strip()
        
        headline = response.xpath('//h1/text()').extract()

        subheader = response.xpath('//meta[@itemprop="description"]/@content').extract()

        sponsor = [remove_tags(s) for s in response.xpath('//div[contains(@class, "sponsored-text")]').extract()]

        syndicator_name = response.xpath('//div[contains(@class, "syndicator-name")]/span/text()').extract()
        
        byline = get_byline(response)

        paragraphs = [remove_tags(p) for p in response.xpath('//p[contains(@class, "element-paragraph")]').extract()]

        yield {
            'url': response.url,
            'date': date,
            'headline': headline,
            'syndicator_name': syndicator_name,
            'byline': byline,
            'paragraphs': paragraphs
        }
