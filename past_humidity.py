import pandas as pd
from datetime import datetime
from tabulate import tabulate

def past_humidity():
    year , month , day = datetime.now().strftime("%Y,%m,%d").split(",")
    prec_no = 44 # 東京都
    block_no = 47662 # 東京

    df2_humidity = pd.DataFrame()
    ## obtain the humidity of last month if today is earlier than 8
    if int(day) < 8:
        url2 = f"https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no={prec_no}&block_no={block_no}&year={year}&month={str(int(month)-1)}&day=&view=p1"
        table2 = pd.read_html(url2)
        df2 = table2[0]
        # 過去1週間の湿度
        df2_humidity = df2["湿度(％)"]
        # headerを変える
        headers = ["平均", "最小"]
        df2_humidity = df2_humidity.set_axis(headers, axis="columns")

    ## obtain the humidity of the past seven days til yesterday
    url = f"https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no={prec_no}&block_no={block_no}&year={year}&month={month}&day=&view=p1"
    table = pd.read_html(url)
    df = table[0]
    # 過去1週間の湿度
    df_humidity = df["湿度(％)"]
    # headerを変える
    headers = ["平均", "最小"]
    df_humidity = df_humidity.set_axis(headers, axis="columns")
    bottom = 0 if int(day) < 8 else (int(day) - 8)

    df_combined = pd.concat([df2_humidity[int(day)-8:], df_humidity[bottom:int(day)-1]], axis=0)
    # print(tabulate(df_combined, headers='keys', tablefmt='psql'))

    ## average humidity of the past week
    sum_humidity = sum(df_combined["平均"])
    ave_humidity = sum_humidity / len(df_combined["平均"])
    return ave_humidity