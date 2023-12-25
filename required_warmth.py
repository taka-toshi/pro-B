import math
import past_humidity
import forecast_temp

weather_data = []
DI_list = []

def check_weather_data(weather_data):
    for temp, humidity in weather_data:
        if temp < -274:
            raise ValueError
        if humidity < 0 or humidity > 100:
            raise ValueError

def calculate_DI(weather_data):
    # 不快指数の計算
    DI_list = []
    for temp, humidity in weather_data:
        DI = 0.81 * temp + 0.01 * humidity * (0.99 * temp - 14.3) + 46.3
        DI_list.append(DI)
    return DI_list

def calculate_required_warmth(DI_list):
    # 必要な暖かさを計算
    # ~50 → 9 * 5
    # 50~55 → 8 * 5
    # 55~60 → 7 * 5
    # 60~65 → 6 * 5
    # 65~70 → 5 * 5
    # 70~75 → 4 * 5
    # 75~80 → 3 * 5
    # 80~85 → 2 * 5
    # 85~ → 1 * 5
    required_warmth = []
    for DI in DI_list:
        DI -= 50
        if DI < 0:
            required_warmth.append(9 * 5)
        elif DI >=35:
            required_warmth.append(1 * 5)
        else:
            rank = 8 - math.floor(DI / 5)
            if type(rank) is not int:
                raise ValueError
            if rank < 2 or rank > 8:
                raise ValueError
            required_warmth.append(rank * 5)
    return required_warmth

def required_warmth():
    humidity = past_humidity.past_humidity() ## int
    forecast = forecast_temp.forecast_temp() ## list
    # forecast = [25,30,10,15,35,15,20]
    weather_data = [
        (forecast[i], humidity) for i in range(len(forecast))
    ]
    # print(weather_data)
    check_weather_data(weather_data)
    DI_list = calculate_DI(weather_data)
    #DI_list = [54,55,59,60,64,65,69,70,74,75,79,80,84,85,89,90]
    # print(DI_list)
    required_warmth = calculate_required_warmth(DI_list)
    return required_warmth ## list