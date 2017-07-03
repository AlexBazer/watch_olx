import requests
import logging
from bs4 import BeautifulSoup
from parse_times import parse

logger = logging.getLogger(__name__)


link = """
https://www.olx.ua/nedvizhimost/arenda-kvartir/odessa/?search%5Bfilter_float_price%3Afrom%5D=8000&search%5Bfilter_float_price%3Ato%5D=11000&search%5Bfilter_float_number_of_rooms%3Afrom%5D=2&search%5Bfilter_float_number_of_rooms%3Ato%5D=3&page=1
"""
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'


class OlxListParser:

    def __init__(self, link):
        response = requests.get(link, headers={'User-agent': user_agent})
        if not response.ok:
            logger.error('Can\'t get ads.')
        self.soup = BeautifulSoup(response.content, "html.parser")

    def get_last_ads_html(self, until=None):
        return [str(item.table) for item in self.filter_by_dtime(until)]

    def get_last_ads_link(self, until=None):
        return [self._extract_link_from_ad(item) for item in self.filter_by_dtime(until)]

    def filter_by_dtime(self, until=None):
        ads = self.get_ads()
        result = []
        for ad in ads:
            dtime = parse(self._extract_time_from_ad(ad))
            logger.info('time to parse: {}'.format(self._extract_time_from_ad(ad)))
            if not dtime:
                continue
            elif until and dtime < until:
                return result

            result.append(ad)

        return result

    def _extract_time_from_ad(self, item):
        return item.select('.color-9')[-1].text.strip()

    def _extract_link_from_ad(self, item):
        return item.select('.link')[0].attrs.get('href')

    def get_ads(self):
        """Will get ads from the first page only
            Ads wont be from the top list
        """
        ads = self.soup.select('table.offers tr.wrap td.offer')
        return [item for item in ads if 'promoted' not in item.attrs.get('class', [])]
