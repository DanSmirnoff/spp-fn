import pandas as pd
import requests
from datetime import datetime, timedelta
from fake_useragent import UserAgent
from IPython import display


class LentaRuParser:

    @staticmethod
    def _get_url(param_dict: dict) -> str:
        hasType = int(param_dict['type']) != 0
        hasBloc = int(param_dict['bloc']) != 0

        url = 'https://lenta.ru/search/v2/process?' \
              + 'from={}&'.format(param_dict['from']) \
              + 'size={}&'.format(param_dict['size']) \
              + 'sort={}&'.format(param_dict['sort']) \
              + 'title_only={}&'.format(param_dict['title_only']) \
              + 'domain={}&'.format(param_dict['domain']) \
              + 'modified%2Cformat=yyyy-MM-dd&' \
              + 'type={}&'.format(param_dict['type']) * hasType \
              + 'bloc={}&'.format(param_dict['bloc']) * hasBloc \
              + 'modified%2Cfrom={}&'.format(param_dict['dateFrom']) \
              + 'modified%2Cto={}&'.format(param_dict['dateTo']) \
              + 'query={}'.format(param_dict['query'])

        return url

    def _get_search_table(self, param_dict: dict) -> pd.DataFrame:
        """
        Returns pd.DataFrame with the search results
        """
        url = self._get_url(param_dict)
        r = requests.get(url, headers={'User-Agent': UserAgent().random})

        try:
            search_table = pd.DataFrame(r.json()['matches'])
            return search_table

        except Exception as e:
            print(e)
            return pd.DataFrame()

    def get_articles(self,
                     param_dict,
                     time_step=10,
                     save_every=5,
                     save_excel=True) -> pd.DataFrame:
        """
        Function for downloading articles at intervals every time_step days.
        Saves the table every save_every * time_step days.

        :param save_excel: bool, optional
            Flag indicating whether to save the downloaded articles as an Excel file. Default is True.

        :param save_every: int, optional
            Interval for saving the table, measured in multiples of time_step days. Default is 5.

        :param time_step: int, optional
            Interval for downloading articles, measured in days. Default is 10.

        :param param_dict: dict
            Dictionary containing query parameters.
            - 'dateFrom' (str): Start date.
            - 'dateTo' (str): End date.
            - 'from' (str): Search output offset.
            - 'size' (str): Article limit, maximum 1000.
            - 'query' (str): Search query (keyword).
            - 'sort' (str): Sorting order of search results.
            - 'title_only' (str): Whether to search only in titles or in full text.
            - 'type' (str): Type of content to search for.
            - 'bloc' (str): Theme's number to search within.
            - 'domain' (str): Domain to restrict the search to.
        """
        param_copy = param_dict.copy()
        time_step = timedelta(days=time_step)
        dateFrom = datetime.strptime(param_copy['dateFrom'], '%Y-%m-%d')
        dateTo = datetime.strptime(param_copy['dateTo'], '%Y-%m-%d')
        if dateFrom > dateTo:
            raise ValueError('dateFrom should be less than dateTo')

        out = pd.DataFrame()
        save_counter = 0

        while dateFrom <= dateTo:
            param_copy['dateTo'] = (dateFrom + time_step).strftime('%Y-%m-%d')

            if dateFrom + time_step > dateTo:
                param_copy['dateTo'] = dateTo.strftime('%Y-%m-%d')

            print('Parsing articles from ' + param_copy['dateFrom'] + ' to ' + param_copy['dateTo'])

            out = pd.concat([out, self._get_search_table(param_copy)], ignore_index=True)
            dateFrom += time_step + timedelta(days=1)
            param_copy['dateFrom'] = dateFrom.strftime('%Y-%m-%d')
            save_counter += 1

            if save_counter == save_every:
                display.clear_output(wait=True)
                out.to_excel("checkpoint_table.xlsx")
                print('Checkpoint saved!')
                save_counter = 0

        if save_excel:
            out.to_excel("lenta_{}_{}.xlsx".format(
                param_dict['dateFrom'],
                param_dict['dateTo']))
        print('Finish')

        return out

