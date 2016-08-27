import random

import scrapy
from rym.items import RymChart
from scrapy import Selector
from scrapy import Spider
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from fake_useragent import UserAgent

ua = UserAgent()


class RymChartSpider(Spider):
    def parse(self, response):
        self.logger.info('Got successful response from {}'.format(response.url))
        releases = Selector(response).xpath('//div[@class="chart_details"]')

        i = 0

        for release in releases:
            self.settings.USER_AGENT = ua.random
            item = RymChart()
            item['artists'] = release.xpath(
                './/a[@class="artist"]/text()').extract()
            item['title'] = release.xpath(
                '//a[@class="album"]/text()').extract()[i]
            try:
                item['year'] = release.xpath(
                    '//span[@class="chart_year"]/text()').re(r'\d+')[i]
            except:
                item['year'] = 2016
            item['genres'] = release.xpath(
                './/*[@class="genre"]/text()').extract()
            item['ranking'] = release.xpath(
                '//span[@class="ooookiig"]/text()').re(r'\d+')[i]
            item['average_rating'] = release.xpath(
                '//*[@class="chart_stats"]/a/b[1]/text()').extract()[i]
            item['number_ratings'] = release.xpath(
                '//*[@class="chart_stats"]/a/b[2]/text()').extract()[i]
            i += 1
            yield item

        if self.pages:
            random.seed()
            random.shuffle(self.pages)
            self.page = self.pages.pop()
            url = self.start_url_1 + str(self.page) + self.start_url_2
            print(url)
            yield scrapy.Request(url, self.parse,
                                 errback=self.errback_httpbin,
                                 dont_filter=True)

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)


class RymTopChartSpider(RymChartSpider):
    name = "rymtop"
    allowed_domains = ["rateyourmusic.com"]
    pages = list(range(1, 125))
    random.seed()
    random.shuffle(pages)
    # start_urls = [
    #     "http://rateyourmusic.com/customchart?page=1&chart_type=top&type=everything&year=alltime&genre_include=1&include_child_genres=1&genres=&include_child_genres_chk=1&include=both&origin_countries=&limit=none&countries=",
    # ]

    start_url_1 = "http://rateyourmusic.com/customchart?page="
    start_url_2 = "&chart_type=top&type=everything&year=alltime&" \
                  "genre_include=1&include_child_genres=1&genres=" \
                  "&include_child_genres_chk=1&include=both&origin_countries=&limit=none&countries="
    page = pages.pop()
    start_urls = [start_url_1 + str(page) + start_url_2]


class RymYearChartSpider(RymChartSpider):
    name = "rymyear"
    allowed_domains = ["rateyourmusic.com"]
    pages = list(range(1, 30))
    random.seed()
    random.shuffle(pages)
    # start_urls = [
    #     "http://rateyourmusic.com/customchart?page=1&chart_type=top&type=everything&year=alltime&genre_include=1&include_child_genres=1&genres=&include_child_genres_chk=1&include=both&origin_countries=&limit=none&countries=",
    # ]

    start_url_1 = "http://rateyourmusic.com/charts/top/album/2016/"
    start_url_2 = ""
    page = pages.pop()
    start_urls = [start_url_1 + str(page)]
