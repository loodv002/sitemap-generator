from dataclasses import dataclass, field
from typing import Union, Tuple, List

@dataclass
class CrawlerConfig:
    index_urls: List[str]
    '''The urls crawler start crawling. Must be given.'''

    allow_domains: List[str]
    '''Allowed domain during crawling, support port and wildcard `*`. Do not include scheme or path.'''

    include_urls: List[str] = field(default_factory=lambda : ['*'])
    '''Included url patterns, support wildcard `*`. Do not include scheme.'''
    
    exclude_urls: List[str] = field(default_factory=list)
    '''Excluded url patterns, support wildcard `*`. Do not include scheme.'''
    
    n_threads: int = 5
    '''Number of crawler worker threads.'''

    n_retries: int = 3
    '''Number of retry for failed requests.'''

    timeout: Union[int, Tuple[int, int]] = (5, 10)
    '''Module `reqeusts` compatible timout values.'''

    verify: bool = True
    '''Verify SSL or not.'''

    proxies: List[str] = field(default_factory=list)
    '''List of module `requests` compatible proxy string. Empty list or list of empty string for no proxy.'''

    user_agent: str = ''
    '''User agent used during request.'''

    cookies: List[Tuple[str, str, str]] = field(default_factory=list)
    '''Cookies in list of tuples `(name, domain, value)`'''

    per_thread_request_gap: int = 1
    '''Per thread time gap between two continuous requests.'''