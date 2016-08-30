import random

from py2neo import Graph
from rym.items import RymChart, RymGenre
from rym.pipelines import Genre
from scrapy import Selector
from scrapy import Spider
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError


class RymTopChartSpider(Spider):
    name = "rymtop"
    allowed_domains = ["rateyourmusic.com"]
    pages = range(1, 125)

    start_urls = [
        "http://rateyourmusic.com/customchart?page="
        + str(page) + "&chart_type=top&type=everything&year=alltime&"
                      "genre_include=1&include_child_genres=1&genres="
                      "&include_child_genres_chk=1&include=both&origin_"
                      "countries=&limit=none&countries="
        for page in pages]
    random.seed()
    random.shuffle(start_urls)

    def parse(self, response):
        self.logger.info('Got successful response from {}'.format(response.url))
        releases = Selector(response).xpath('//div[@class="chart_detail"]')
        print(releases)
        for index, release in enumerate(releases):
            item = RymChart()
            item['artists'] = release.xpath(
                './/a[@class="artist"]/text()').extract()
            item['title'] = release.xpath(
                '//a[@class="album"]/text()').extract()[index]
            try:
                item['year'] = release.xpath(
                    '//span[@class="chart_year"]/text()').re(r'\d+')[index]
            except KeyError:
                item['year'] = 2016
            item['genres'] = release.xpath(
                './/*[@class="genre"]/text()').extract()
            item['ranking'] = Selector(response).xpath(
                '//span[@class="ooookiig"]/text()').re(r'\d+')[index]
            item['average_rating'] = Selector(response).xpath(
                '//*[@class="chart_stats"]/a/b[1]/text()').extract()[index]
            item['number_ratings'] = Selector(response).xpath(
                '//*[@class="chart_stats"]/a/b[2]/text()').extract()[index]
            yield item


class RymYearChartSpider(Spider):
    name = "rymyear"
    allowed_domains = ["rateyourmusic.com"]
    pages = range(1, 30)  # ranking list has 30 pages, 1956 is first year with 30 full pages
    years = range(1922, 2016)  # First release in 1922

    # lambda is to avoid NameError
    start_urls = (
        lambda pages=pages, years=years:
        ["http://rateyourmusic.com/charts/top/album/" + str(year) + "/" + str(page)
         for year in years for page in pages])()
    # Because of banning for scraping
    random.seed()
    random.shuffle(start_urls)

    def parse(self, response):
        self.logger.info('Got successful response from {}'.format(response.url))
        releases = Selector(response).xpath('//div[@class="chart_details"]')
        print(releases)
        for index, release in enumerate(releases):
            item = RymChart()
            item['artists'] = release.xpath(
                './/a[@class="artist"]/text()').extract()
            item['title'] = release.xpath(
                '//a[@class="album"]/text()').extract()[index]
            try:
                item['year'] = release.xpath(
                    '//span[@class="chart_year"]/text()').re(r'\d+')[index]
            except KeyError:
                item['year'] = 2016
            item['genres'] = release.xpath(
                './/*[@class="genre"]/text()').extract()
            item['ranking'] = release.xpath(
                '//span[@class="ooookiig"]/text()').re(r'\d+')[index]
            item['average_rating'] = release.xpath(
                '//*[@class="chart_stats"]/a/b[1]/text()').extract()[index]
            item['number_ratings'] = release.xpath(
                '//*[@class="chart_stats"]/a/b[2]/text()').extract()[index]
            yield item


class RymGenreSpider(Spider):
    name = "rymgenre"
    allowed_domains = ["rateyourmusic.com"]
    graph = Graph("http://localhost:7474/", password="01041990")

    start_urls = ["http://rateyourmusic.com/genre/" + x.name.replace(" ", "+") for x in list(Genre.select(graph))]

    random.seed()
    random.shuffle(start_urls)

    def parse(self, response):
        self.logger.info('Got successful response from {}'.format(response.url))
        sel = Selector(response)
        item = RymGenre()
        item['name'] = sel.xpath('*//table[@class="mbgen"]/tr/td[2]/div/div/text()').extract()[0]
        item['supergenres'] = sel.xpath(
            '*//table[@class="mbgen"][1]/tr/td[2]/div/a/text()').extract()
        item['subgenres'] = sel.xpath(
            '*//table[@class="mbgen"][1]/tr/td[2]/div/div/div/a/text()').extract()

        yield item


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
