# Crawler

## 實驗重現
- CPU: Intel(R) Core(TM) i5-1135G7 CPU (2.40GHz 8 Core)
- RAM: 16G

## 實驗步驟
將以下 Python code 存檔，置於 repo 根目錄。其中，測試用的四個網站的 `config` 設定，可於 [`/crawler_test_config.py`](/crawler_test_config.py) 中取得。
```python
from crawler import *
config = CrawlerConfig(
    ...
)

cr = Crawler(config)
cr.main() 
```

透過 `time` 測試執行時長即可。
```shell
$ time python <filename>
```

## 實驗結果 (單位: 秒)

| N_threads​         | 1    | 2    | 3    | 4    | 5    | 6    |
| ----------------- | ---- | ---- | ---- | ---- | ---- | ---- |
| 校網(資訊公開專區) | 525.78 | 266.32 | 176.34 | 133.92 | 109.44 | 87.03 |
| 系網(不含公告區)​   | 1424.87 | 711.89 | 473.24 | 355.09 | 289.59 | 236.94 |
| Python 3.13 文件  | 1228.97 | 669.13 | 389.98 | 323.36 | 258.83 | 209.53 |
| 系網(公告區)​       | 2142.83 | 1072.32 | 715.70 | 537.15 | 433.19 | 361.67 |

