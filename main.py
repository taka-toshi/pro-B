from amplify import (
    BinaryPoly,
    BinaryQuadraticModel,
    Solver,
    SymbolGenerator,
)
from amplify.client import FixstarsClient

# 変数配列の生成
gen = SymbolGenerator(BinaryPoly)
q = gen.array(shape=(2,2,2))
print(q)

# バイナリ多項式の構築
f = 1 - q[0][0][0]
model = BinaryQuadraticModel(f)

# イジングマシンクライアントの設定
client = FixstarsClient()

token_file = "./token.txt"
with open(token_file) as f:
    client.token = f.readline()
f.close()

client.parameters.timeout = 1000  # タイムアウト1秒

# ソルバーの実行
solver = Solver(client)
result = solver.solve(model)

# 結果の解析
for solution in result:
    print(f"q = {q.decode(solution.values)}")