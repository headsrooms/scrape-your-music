from fake_useragent import UserAgent
from scrapy.utils.project import get_project_settings

ua = UserAgent()


class RandomUserAgentMiddleware(object):
    @staticmethod
    def process_request():
        get_project_settings().USER_AGENT = ua.random
