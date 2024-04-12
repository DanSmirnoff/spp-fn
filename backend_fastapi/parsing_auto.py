import schedule
import time
from fastapi_service.services import *
from datetime import datetime


def run_parse_lenta():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    print("Parsing lenta.ru at", current_time)

    current_date = now.strftime('%Y-%m-%d')
    parse_lenta(dateFrom=current_date, dateTo=current_date)


def run_parse_imoex():
    print("Parsing IMOEX at 19:00 by Moscow time")
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    parse_imoex(dateFrom=current_date, dateTo=current_date)


# Schedule lenta parsing every 30 minutes
schedule.every(30).minutes.do(run_parse_lenta)

# Schedule imoex parsing at 19:00 by Moscow time
schedule.every().day.at("19:00").do(run_parse_imoex)

while True:
    schedule.run_pending()
    time.sleep(1)

