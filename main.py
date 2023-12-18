import random
import sys

from amplify import (BinaryPoly, BinaryQuadraticModel, Solver, SymbolGenerator, sum_poly)
from amplify.client import FixstarsClient

# ========================================================
T = 5 # 0-4の5日間
C = 3 # c = 0 : ズボン, c = 1 : トップス, c = 2 :アウター
K = 7 # 0-6の種類

W = [0] * T #各日の必要な暖かさ
for t in range(T):
    W[t] = random.randint(1,9)*5

w = [[0] * K for _ in range(C)] #各種類の暖かさ
M = [0] * C # 各cについてwのmax
m = [0] * C # 各cについてwのmin
for c in range(C):
    if c != C-1:
        for k in range(K):
            w[c][k] = random.randint(2,16)
    else:
        for k in range(K):
            w[c][k] = random.randint(10,16)
    M[c] = max(w[c])
    m[c] = min(w[c])

w_bar = [[0] * K for _ in range(C)] #各種類の暖かさ　標準化
for c in range(C):
    for k in range(K):
        w_bar[c][k] = (w[c][k] - m[c]) / (M[c] - m[c])
# ========================================================

def main():
    # 変数配列の生成
    gen = SymbolGenerator(BinaryPoly)
    q = gen.array(shape=(T,C,K))
    # バイナリ多項式の構築

    # 選んだ服の暖かさ平均（ボトムズc=0とトップスc=1のみ）
    A = [0] * T
    for t in range(T):
        A[t] = sum_poly(C-1, lambda c: sum_poly(K, lambda k: w[c][k] * q[t, c, k])) / (C-1)

    # 分散（ボトムズとトップス）
    D = sum_poly(T, lambda t: 
                sum_poly(C-1, lambda c: 
                        ((sum_poly(K, lambda k: w[c][k] * q[t, c, k])) - A[t]) ** 2) / (C-1))

    # アウターの暖かさ（着るなら平均A[t]に近くなるようにする）
    E = sum_poly(T, lambda t: 
                (sum_poly(K, lambda k: w[2][k] * q[t, 2, k]) - A[t] * sum_poly(K, lambda k: q[t, 2, k])) ** 2)

    # トップスとズボンはone-hot
    f1 = sum_poly(T, lambda t: 
                (sum_poly(C-1, lambda c: 
                        (sum_poly(K, lambda k: q[t, c, k]) - 1) ** 2)))
    # アウター ≤ 1
    f2 = sum_poly(T, lambda t: (1- sum_poly(K, lambda k: q[t, 2, k]) * 2) ** 2 -1)
    # 前日と同じ服は着ない
    f3 = sum_poly(T, lambda t: (sum_poly(C, lambda c: (sum_poly(K, lambda k: q[t, c, k] * q[(t+1)%T, c, k])))))

    # 目的関数の設定
    # 暖かさ
    g = sum_poly(T, lambda t: (sum_poly(C, lambda c: sum_poly(K, lambda k: w[c][k] * q[t, c, k])) - W[t]) ** 2)

    # パラメータの重さ調整
    alpha = 10
    beta = 0.01
    gamma = 3
    model = BinaryQuadraticModel(alpha*D+beta*E+100*(f1+f2+f3)+gamma*g)

    # イジングマシンクライアントの設定
    client = FixstarsClient()
    client.token = my_token
    client.parameters.timeout = 5000  # タイムアウト5秒

    # ソルバーの実行
    solver = Solver(client)
    result = solver.solve(model)

    # 結果の解析
    for solution in result:
        print(f'energy = {solution.energy}')
        q_array = q.decode(solution.values)
        print("============")
        check_array(q_array)
        print("============")
        print_array(q_array, alpha , beta, gamma)
        break # solutionが複数の場合も1つだけ出力

def check_array(q_array):
    # トップスとズボンはone-hot
    for t in range(T):
        for c in range(C-1):
            sum_k = 0
            for k in range(K):
                sum_k += q_array[t][c][k]
            if sum_k != 1:
                print(f"{t+1}日目の(c={c}) != 1")

    # アウター <= 1
    for t in range(T):
        sum_k = 0
        for k in range(K):
            sum_k += q_array[t][2][k]
        if sum_k > 1:
            print(f"{t+1}日目のアウター(c=2) > 1")

    # 前日と同じ服は着ない
    for t in range(T):
        for c in range(C):
            for k in range(K):
                if q_array[t][c][k] * q_array[(t+1)%T][c][k] != 0:
                    print(f"{t+1}・{(t+2)%T}日目の服(c={c}) != 0")

def print_array(q_array, alpha , beta, gamma):
    # print w
    print("w    ",end="|")
    for c in range(C):
        for k in range(K):
            print(f"{w[c][k]:4d}",end=",")
        print("|",end="")
    print()
    # print w_bar
    print("w_bar",end="|")
    for c in range(C):
        for k in range(K):
            print(f"{w_bar[c][k]:.2f}",end=",")
        print("|",end="")
    print(" W  sum_w  差^2  A    D      E")

    sum_D = 0.0
    sum_E = 0.0
    sum_sa_sa = 0
    for t in range(T):
        sum_w = 0
        sum_w_12 = 0.0
        A = 0.0
        E = 0.0
        E_exist = False
        print(f"{t+1}日目",end="|")
        for c in range(C):
            for k in range(K):
                if q_array[t][c][k] == 1:
                    sum_w += w[c][k]
                    if c!= C-1:
                        sum_w_12 += w[c][k]
                    else:
                        E_exist = True
                        E = w[c][k]
                    print(" ◯  ",end=",")
                else:
                    print("    ",end=",")
            print("|",end="")
        A = sum_w_12 / (C-1)
        if E_exist:
            E = (E-A)**2
        D = 0.0
        for c in range(C-1):
            for k in range(K):
                if q_array[t][c][k] == 1:
                    D += (w[c][k] - A)**2
        D /= (C-1)
        sum_D += D
        sum_E += E
        sa_sa = (W[t]-sum_w)**2
        sum_sa_sa += sa_sa
        print(f" {W[t]:2d}  {sum_w:2d}   {sa_sa:3d}   {A:.2f}  {D:.3f}  {E:.3f}")
    print(f"sum差^2*γ({gamma}): {gamma*sum_sa_sa:.1f}\nsumD*α({alpha}): {alpha*sum_D:.5f}\nsumE*β({beta}): {beta*sum_E:.3f}")
    print(f"合計: {alpha*sum_D+beta*sum_E+gamma*sum_sa_sa}")

if __name__ == '__main__':
    my_token = ""
    token_file = "./token.txt"
    with open(token_file) as f:
        my_token = f.readline()
    f.close()
    main()