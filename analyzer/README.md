# Analyzer
## AnalyzerConfig 說明
### damping

設定 PageRank 演算法的 damping factor，預設為 0.85（與原始論文相同）

### convergence

設定 PageRank 演算法中的 convergence，其意義為停止迭代計算的數值變動量閾值，預設值為 $10^{-7}$

### algorithm

設定使用的 PageRank 版本，目前支援 `AnalyzeAlgorithm.PAGERANK_PY`（serial 版本）、`AnalyzeAlgorithm.PAGERANK_PYMAT`（使用矩陣運算的 serial 版本）、`AnalyzeAlgorithm.PAGERANK_NP`（NumPy 版本）、`AnalyzeAlgorithm.PAGERANK_CUPY`（CuPy 版本）四種，預設使用 serial 版本

## 實驗說明
### 實驗環境

- 平台：Google Colab
    - CPU：Intel(R) Xeon(R) CPU @ 2.00GHz 2 Core
    - 記憶體：12.7 GB
    - GPU：Tesla T4
- CUDA 版本：12.2
- Python 版本：3.10.12
    - NumPy 版本：1.26.4
    - CuPy 版本：12.2.0

### 實驗步驟

1. 準備以下資料夾及檔案結構，上傳至 Colab 平台

```
.
├── analyzer
│   ├── __init__.py
│   ├── analyzer.py
│   ├── config.py
│   └── pagerank.py
├── crawler
│   ├── __init__.py
│   ├── config.py
│   ├── crawler.py
│   ├── graph_manager.py
│   └── url_utils.py
├── docs.python.org_only313.pkl
├── info.nycu.edu.tw.pkl
├── random_100000.pkl
├── www.cs.nycu.edu.tw_ann.pkl
└── www.cs.nycu.edu.tw_oth.pkl
```

2. 根據要測試的網站類型，替換以下程式碼中的 `pickle.load(open('xxx.pkl', 'rb'))` 部分

```python
import pickle

gm = pickle.load(open('info.nycu.edu.tw.pkl', 'rb'))

from analyzer import *
from time import time

start = time()
az = Analyzer(graph_manager=gm, config=AnalyzerConfig(algorithm=AnalyzeAlgorithm.PAGERANK_PY))
urlweight = az.main()
print('Time:', time() - start)
# print(urlweight[50:60])

print('==============================')

start = time()
az = Analyzer(graph_manager=gm, config=AnalyzerConfig(algorithm=AnalyzeAlgorithm.PAGERANK_PYMAT))
urlweight2 = az.main()
print('Time:', time() - start)
# print(urlweight2[50:60])

print('==============================')

start = time()
az = Analyzer(graph_manager=gm, config=AnalyzerConfig(algorithm=AnalyzeAlgorithm.PAGERANK_NP))
urlweight3 = az.main()
print('Time:', time() - start)
# print(urlweight3[50:60])

print('==============================')

start = time()
az = Analyzer(graph_manager=gm, config=AnalyzerConfig(algorithm=AnalyzeAlgorithm.PAGERANK_CUPY))
urlweight4 = az.main()
print('Time:', time() - start)
# print(urlweight4[50:60])
```

3. 先執行一次上述的程式碼做為 warmup，再執行三次並取時間平均值