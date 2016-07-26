from rym.items import RymRelease
from scrapy import Selector
from scrapy import Spider


class RymSpider(Spider):
    name = "rym"
    allowed_domains = ["http://rateyourmusic.com/"]
    start_urls = [
        "http://webcache.googleusercontent.com/search?q=cache:rateyourmusic.com/customchart?page=1&chart_type=top&type=everything&year=alltime&genre_include=1&include_child_genres=1&genres=&include_child_genres_chk=1&include=both&origin_countries=&limit=none&countries=",
    ]

    def parse(self, response):
        releases = Selector(response).xpath('//div[@class="chart_details"]')

        i = 0
        for release in releases:
            item = RymRelease()
            item['artists'] = release.xpath(
                './/a[@class="artist"]/text()').extract()
            item['title'] = release.xpath(
                '//a[@class="album"]/text()').extract()[i]
            item['year'] = release.xpath(
                '//span[@class="chart_year"]/text()').extract()[i]
            item['genres'] = release.xpath(
                 './/*[@class="genre"]/text()').extract()
            i += 1
            yield item
