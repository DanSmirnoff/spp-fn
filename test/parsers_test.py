from datetime import datetime
from streamlit_app.stocks import get_stocks_info


info = get_stocks_info('IMOEX', str(datetime.now().date()), str(datetime.now().date()), '10m')

print(info)
