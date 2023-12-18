import math

weather_data = []
DI_list = []

#def get_weather_data(days):

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
    # ~55 → 8 * 5
    # 55~60 → 7 * 5
    # 60~65 → 6 * 5
    # 65~70 → 5 * 5
    # 70~75 → 4 * 5
    # 75~80 → 3 * 5
    # 80~85 → 2 * 5
    # 85~ → 1 * 5
    required_warmth = []
    for DI in DI_list:
        DI -= 55
        if DI < 0:
            required_warmth.append(8 * 5)
        elif DI >=30:
            required_warmth.append(1 * 5)
        else:
            rank = 7-math.floor(DI / 5)
            if type(rank) is not int:
                raise ValueError
            if rank < 2 or rank > 7:
                raise ValueError
            required_warmth.append(rank * 5)
    return required_warmth

def main():
    weather_data = [
        (24, 30),(20, 59),(21, 30),(19, 10),(17, 60),(15, 55),(13, 50)
    ]
    check_weather_data(weather_data)
    DI_list = calculate_DI(weather_data)
    #DI_list = [54,55,59,60,64,65,69,70,74,75,79,80,84,85,89,90]
    print(DI_list)
    required_warmth = calculate_required_warmth(DI_list)
    print(required_warmth)

if __name__ == '__main__':
    main()