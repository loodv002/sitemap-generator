from crawler import *

cr = Crawler(CrawlerConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.70',
    index_urls=['https://info.nycu.edu.tw/'],
    allow_domains=['*info.nycu.edu.tw'], # Allow "info.nycu.edu.tw" and "*.info.nycu.edu.tw"
))
cr.main()