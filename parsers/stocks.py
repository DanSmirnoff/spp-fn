import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class InvestingComParser:
    def __init__(self):
        self.link_types = {
            'stock': 'equities',
            'index': 'indices'
        }
        self.brackets_pattern = re.compile(r'\((.*?)\)')

    def _get_url(self, ticker_type: str, ticker: str) -> str:
        return f'https://ru.investing.com/{self.link_types[ticker_type]}/{ticker}'

    def _get_ticker(self, soup) -> str:
        ticker = soup.find('h1', {
            'class': 'mb-2.5 text-left text-xl font-bold leading-7 text-[#232526] md:mb-2 md:text-3xl md:leading-8 rtl:soft-ltr'
        }).text
        ticker = re.findall(self.brackets_pattern, ticker)[0]
        return ticker

    def _get_time(self, soup) -> str:
        time = soup.find('time').text
        return time

    def _get_soup(self, ticker_type: str, ticker: str):
        url = self._get_url(ticker_type, ticker)

        response = requests.get(url, headers={'User-Agent': UserAgent().random})
        if response.status_code != 200:
            print("Status code:", response.status_code)
            return None

        return BeautifulSoup(response.text, 'html.parser')

    def get_info(self, ticker_type: str, ticker: str) -> tuple | None:
        soup = self._get_soup(ticker_type, ticker)

        try:
            price = soup.find('div', {
                'class': 'text-5xl/9 font-bold text-[#232526] md:text-[42px] md:leading-[60px]'}).text
        except AttributeError:
            try:
                price = soup.find('div', {
                    'class': 'text-5xl/9 font-bold text-[#232526] md:text-[42px] md:leading-[60px] bg-negative-light'}).text
            except AttributeError:
                try:
                    price = soup.find('div', {
                        'class': 'text-5xl/9 font-bold text-[#232526] md:text-[42px] md:leading-[60px] bg-negative-light'}).text
                except AttributeError:
                    print("")
                    return None

        ticker = self._get_ticker(soup)
        time = self._get_time(soup)

        return ticker, price, time

