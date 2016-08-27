from fake_useragent import UserAgent
from scrapy.utils.project import get_project_settings

ua = UserAgent()


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        get_project_settings().USER_AGENT = ua.random
