def update_bert_pca():
    """
    берет из lenta_news.csv донные за день
    прогоняет bert и pca и обновляет через DataLoader файл bert_pca.csv
    """
    pass


def compute_imoex_stats():
    """
    берет данные по imoex за сегодня и считает статистики
    обновляет файл stats_imoex_open.csv
    """


def unite_stats_pca():
    """
    объединяет данные из stats_imoex_open.csv и bert_pca.csv за сегодня
    и обновляет файл dataset.csv
    """

