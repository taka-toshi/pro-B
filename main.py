import random
import sys
from amplify import *
from amplify.client import FixstarsClient

my_token = ""
token_file = "./token.txt"
with open(token_file) as f:
    my_token = f.readline()
f.close()

# ========================================================
T = 5 # 0-4の5日間
C = 3 # c = 0 : ズボン, c = 1 : トップス, c = 2 :アウター
K = 5 # 0-4の種類

W = [0] * T #各日の必要な暖かさ
for t in range(T):
    W[t] = random.randint(10,50)

w = [[0] * K for _ in range(C)] #各種類の暖かさ
M = [0] * C # 各cについてwのmax
m = [0] * C # 各cについてwのmin
for c in range(C):
    for k in range(K):
        w[c][k] = random.randint(3,17)
    M[c] = max(w[c])
    m[c] = min(w[c])

w_bar = [[0] * K for _ in range(C)] #各種類の暖かさ　標準化
for c in range(C):
    for k in range(K):
        w_bar[c][k] = (w[c][k] - m[c]) / (M[c] - m[c])
# ========================================================

# 変数配列の生成
gen = SymbolGenerator(BinaryPoly)
q = gen.array(shape=(T,C,K))
# バイナリ多項式の構築

# トップスとズボンはone-hot
f1 = sum_poly(T, lambda t: (sum_poly(C-1, lambda c: (sum_poly(K, lambda k: q[t, c, k]) - 1) ** 2)))
# アウター ≤ 1
f2 = sum_poly(T, lambda t: (1- sum_poly(K, lambda k: q[t, 2, k]) * 2) ** 2 -1)
# 前日と同じ服は着ない
f3 = sum_poly(T, lambda t: (sum_poly(C, lambda c: (sum_poly(K, lambda k: q[t, c, k] * q[(t+1)%T, c, k])))))

# 目的関数の設定
# 暖かさ
h = sum_poly(T, lambda t: (sum_poly(C, lambda c: sum_poly(K, lambda k: w[c][k] * q[t, c, k])) - W[t]) ** 2)

model = BinaryQuadraticModel(f1+f2+f3+h)

# イジングマシンクライアントの設定
client = FixstarsClient()
client.token = my_token
client.parameters.timeout = 1000  # タイムアウト1秒

# ソルバーの実行
solver = Solver(client)
result = solver.solve(model)

# 結果の解析
for solution in result:
    print(f"q = {q.decode(solution.values)}")
    print(f'energy = {solution.energy}')