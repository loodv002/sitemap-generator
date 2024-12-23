from crawler import *
from analyzer import *
from generator import *

# Run Crawler in 2 threads
cr = Crawler(CrawlerConfig(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.70',
    index_urls=['https://info.nycu.edu.tw/'],
    allow_domains=['*info.nycu.edu.tw'],
    n_threads=2
))
cr.main() 


# Run PageRank Algo.
az = Analyzer(graph_manager=cr.graph_manager, config=AnalyzerConfig())
urlweight = az.main() 
print(urlweight)


# Generate sitemap.xml in serial
sm = SiteMap()
sm.main(urlweight)

# Generate sitemap.xml in parallel
sm = SiteMapParallel()
sm.main(urlweight)