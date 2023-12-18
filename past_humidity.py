from datetime import datetime
from collections import OrderedDict

import pandas as pd
from tabulate import tabulate

dict_humidity = OrderedDict()
year , month , day = datetime.now().strftime("%Y,%m,%d").split(",")
prec_no = 44 # 東京都
block_no = 47662 # 東京
url = f"https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no={prec_no}&block_no={block_no}&year={year}&month={month}&day=&view=p1"

#if int(day) < 8:
#    url2 = f"https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no={prec_no}&block_no={block_no}&year={year}&month={month-1}&day=&view=p1"

table = pd.read_html(url)
df = table[0]
# 過去1週間の湿度
df_humidity = df["湿度(％)"]
# headerを変える
headers = ["平均", "最小"]
df_humidity = df_humidity.set_axis(headers, axis="columns")
for i, humidity in enumerate(df_humidity["平均"]):
    if i+1 > int(day) -1:
        break
    elif i+1 > int(day) -8:
        dict_humidity[i+1] = humidity

for key, val in dict_humidity.items():
    print(key, val)
