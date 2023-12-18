from datetime import datetime

import pandas as pd
import requests
from tabulate import tabulate

# get area codes
url = "http://www.jma.go.jp/bosai/common/const/area.json"
with requests.get(url) as response:
    area = response.json()

# search for pref_code
pref = "東京都" # inputにする？？
pref_code = [k for k, v in area["offices"].items() if v["name"] == pref][0]

url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{pref_code}.json"

with requests.get(url) as response:
    forecast = response.json()

f1 = forecast[0]["timeSeries"][2]
f2 = forecast[1]["timeSeries"][1]

forecast_area = ""

f1_area = [wf1["area"]["name"] for wf1 in f1["areas"]]
f1_and_f2_area = []
for wf2 in f2["areas"]:
    if wf2["area"]["name"] in f1_area:
        f1_and_f2_area.append(wf2["area"]["name"])

if len(f1_and_f2_area) == 0:
    forecast_area = f2["areas"][0]["area"]["name"]
elif len(f1_and_f2_area) == 1:
    forecast_area = f1_and_f2_area[0]
else:
    print("please select")
    for i, area in enumerate(f1_and_f2_area):
        print("" + str(i) + ": " + area + "")
    forecast_area = f1_and_f2_area[int(input())] #inputじゃなくする？？

print(forecast_area)

#=======================================================================
# 明日の天気予報
for wf1 in f1["areas"]:
    if wf1["area"]["name"] == forecast_area:
        print(wf1["area"]["code"])
        tomorrow_temps = wf1["temps"]

# 今日の日付を取得
today = datetime.now().strftime('%Y-%m-%d')
# 今日の日付分のデータを削除
valid1 = [date for date in f1["timeDefines"] if today not in date]
for _ in range(len(f1["timeDefines"])-len(valid1)):
    tomorrow_temps.remove(tomorrow_temps[0])

for i, tt in enumerate(tomorrow_temps):
    tomorrow_temps[i] = int(tt)
#df = pd.DataFrame({"temps":tomorrow_temps}, index=valid1)
#print(tabulate(df, headers="keys", tablefmt="psql"))

#=======================================================================
# 1週間の天気予報
for wf2 in f2["areas"]:
    if wf2["area"]["name"] == forecast_area:
        tempsMin = wf2["tempsMin"]
        #tempsMinUpper = wf2["tempsMinUpper"]
        #tempsMinLower = wf2["tempsMinLower"]
        tempsMax = wf2["tempsMax"]
        #tempsMaxUpper = wf2["tempsMaxUpper"]
        #tempsMaxLower = wf2["tempsMaxLower"]

valid2 = [date.split("T")[0] for date in f2["timeDefines"]]

if tempsMin[0] == "":
    tempsMin[0] = min(tomorrow_temps)
    tempsMax[0] = max(tomorrow_temps)

df = pd.DataFrame({"min":tempsMin, "max":tempsMax}, index=valid2)
print(tabulate(df, headers="keys", tablefmt="psql"))