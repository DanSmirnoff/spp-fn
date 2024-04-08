import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm


t_min, t_max = 0, 10000      # Определяем временной интервал
t = np.arange(t_min, t_max)  # Задаем массив значений времени
N = t_max//2                 # Выбираем срез времени для дальнейших тестов


def wiener(t: list) -> list:
    '''
    Генерирует Винеровский процесс от t_min до t_max
    '''
    t_min, t_max = t[0], t[-1]
    dWiener = np.random.randn(t_max)/np.sqrt(t_max)
    dWiener = np.insert(dWiener, 0, 0)
    Wiener = np.cumsum(dWiener)[t_min:]
    return Wiener


def stocks(Wiener: list, loc: float, scale: float) -> list:
    '''
    Генерирует геометрическое Броуновское движение
    с параметрами loc и scale
    '''
    t = np.array(list(range(len(Wiener))))
    S = np.exp((loc-scale**2/2)*t+scale*Wiener)
    return S


def get_section(N: int = N, N_max: int = t_max, count: int = 1000000) -> list:
    """
    Делает срез в момент времени N
    count раз
    """
    if N>N_max:
        print('N>N_max')
        raise Exception
    values = []
    for _ in tqdm(range(count)):
        values.append(wiener(t)[N])
    return values
