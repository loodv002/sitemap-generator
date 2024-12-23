from crawler import CrawlerConfig

# 校網(資訊公開專區)
config = CrawlerConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.70',
    index_urls=['https://info.nycu.edu.tw/', 'https://info.nycu.edu.tw/infopublic/ir-sys/ir-sys1/', 'https://info.nycu.edu.tw/infopublic/fund/fund1/', 'https://info.nycu.edu.tw/infopublic/fee/fee1/', 'https://info.nycu.edu.tw/infopublic/oth-info/oth-info1/', 'https://info.nycu.edu.tw/infopublic/control/control1/'],
    allow_domains=['*info.nycu.edu.tw'],
)

# '系網(不含公告區)'
config = CrawlerConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.70',
    index_urls=['https://www.cs.nycu.edu.tw/', 'https://www.cs.nycu.edu.tw/members/prof', 'https://www.cs.nycu.edu.tw/intro', 'https://www.cs.nycu.edu.tw/research', 'https://www.cs.nycu.edu.tw/admission', 'https://www.cs.nycu.edu.tw/education'],
    allow_domains=['www.cs.nycu.edu.tw'],
    exclude_urls=['www.cs.nycu.edu.tw/announcements*', '*locale=*'],
)

# 'Python 3.13 文件'
config = CrawlerConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.70',
    index_urls=['https://docs.python.org/zh-tw/3/', 'https://docs.python.org/zh-tw/3/library/posix.html', 'https://docs.python.org/zh-tw/3/library/numbers.html', 'https://docs.python.org/zh-tw/3/library/math.html', 'https://docs.python.org/zh-tw/3/library/platform.html', 'https://docs.python.org/zh-tw/3/library/index.html'],
    allow_domains=['docs.python.org'],
    include_urls=['docs.python.org/zh-tw/3/*'],
)

# '系網(公告區)'
config = CrawlerConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.70',
    index_urls=['https://www.cs.nycu.edu.tw/announcements'],
    allow_domains=['www.cs.nycu.edu.tw'],
    include_urls=['www.cs.nycu.edu.tw/announcements*'],
    exclude_urls=['*locale=*'],
)