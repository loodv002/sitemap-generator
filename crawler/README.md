# CrawlerConfig

## 爬取範圍相關參數

### `index_urls` (必填)
* 型別: `List[str]`
* 初始請求網址，例如網站首頁。
* 給定多個初始網址，能縮短程式開始執行到爬蟲線程滿載的耗時。
* 初始網址應在同一爬取範圍內(即，所產生的連結圖應連通)。

### `allow_domains` (必填)
* 型別: `List[str]`
* 限制爬取範圍，一個連結網址僅在其域名與此項列表任一項目匹配時，才會被爬取。
* 項目不可包含協議 (ex: `http://`)、路徑、或查詢參數，否則匹配失敗。
* 支援 `*` 配對。
* 範例:
  * `allow_domains = ['*a.com']` 可匹配以下網址
    * `http://a.com/some/path/`
    * `https://sub.domain.a.com/?query=param`

### `include_urls`
* 型別: `List[str]`
* 預設值: `['*']` (匹配任何網址)
* 限制爬取範圍，一個連結網址僅在其域名、路徑、查詢參數與此項列表任一項目匹配時，才會被爬取。
* 項目不可包含協議，否則匹配失敗。
* 支援 `*` 配對。
* 範例:
  * `include_urls = ['a.com/path?page=*']` 無法匹配以下網址
    * `https://sub.a.com/path?page=123` (因域名不匹配)
    * `http://a.com/some/path/` (因參數缺失而不匹配)

### `exclude_urls`
* 型別: `List[str]`
* 預設值: `[]` (不匹配任何網址)
* 限制爬取範圍，一個連結網址之域名、路徑及查詢參數與此項列表任一項目匹配時，**不會**被爬取。
* 項目不可包含協議，否則匹配失敗。
* 支援 `*` 配對。

> 綜合上述設定，
> * 一個網址在爬取範圍內，僅當
>   * 網址匹配 allow_domains 之任一項目，且
>   * 網址匹配 include_urls 之任一項目，且
>   * 網址不匹配 exclude_urls 之任一項目。
> 
> * 一個網址會被爬取，僅當
>   * 網址在爬取範圍內，且
>   * 網址能從 index_urls 之任一項目開始，透過數個在爬取範圍內的連結造訪，且
>   * 網址的 HTTP 回應格式為 HTML。

## 爬蟲線程與 HTTP 相關參數

### `n_threads`
* 型別: `int`
* 預設值: `5`
* 爬蟲子線程數。

### `n_retries`
* 型別: `int`
* 預設值: `3`
* HTTP 請求重試次數，`0` 為不重試。兩次請求重試的間隔秒數為 2 的指數。
  
### `timeout`
* 型別: `int` 或 `Tuple[int, int]`
* 預設值: `(5, 10)`
* 相容 Python `requests` 模組的 `timeout` 設定。
  * 若其值為單一整數 `x`，則 connect timeout 與 read timeout 皆為 `x` 秒。
  * 若其值為兩整數元組 `(x,y)`，則 connect timeout 為 `x` 秒，read timeout 為 `y` 秒。

### `verify`
* 型別: `bool`
* 預設值: `True`
* 是否驗證 https 的 SSL 證書。

### `proxies`
* 型別: `List[str]`
* 預設值: `[]`
* 爬蟲線程所用的代理。
  * 若串列為空，所有線程不使用代理。
  * 若串列不為空，則線程依其編號之模除分配代理字串。
    * 若分配到的代理字串為空，則該線程不使用代理。
    * 否則，代理字串應相容於 Python `requests` 模組的 `proxies` 設定，例如 `socks4://a.b.c.d`。
* 舉例:
  * `n_threads = 5, proxies = ['socks4://1.1.1.1', 'socks5://2.2.2.2', 'socks5://3.3.3.3']`，則代理分配如下
  
    | 代理 | 線程編號 |
    |---|---|
    | `socks4://1.1.1.1` | 0, 3 |
    | `socks5://2.2.2.2` | 1, 4 |
    | `socks5://3.3.3.3` | 2 |

  * `n_threads = 2, proxies = ['', 'socks5://1.1.1.1']` 表示線程 0 不使用代理，線程 1 使用代理 `socks5://1.1.1.1`。

### `user_agent`
* 型別: `str`
* 預設值: `''`
* 若 `user_agent` 非空字串，使用此字串替換 Python `requests` 模組內建的使用者代理。
* 由於內建的使用者代理容易被封鎖，建議給予主流瀏覽器的使用者代理，增加爬蟲成功率。

### `cookies`
* 型別: `List[Tuple[str, str, str]]`
* 預設值: `[]`
* 請求所攜帶的 cookies。串列中，每個元組的三個字串表示一個 cookie 的名稱、作用的網域、cookie 的值。

### `per_thread_request_gap`
* 型別: `int`
* 預設值: `1`
* 不同請求間的間隔秒數，每個爬蟲線程各自計算。
* 單一請求的重試不受此間隔影響。