from urllib.parse import urlparse, urljoin
import re

from typing import List

def _check_pattern_with_wildcard(pattern: str, target: str):
    pattern = pattern.replace('/', '\\/')
    pattern = pattern.replace('.', '\\.')
    pattern = pattern.replace('*', '.*')
    pattern = f'^{pattern}$'
    return re.match(pattern, target) is not None

def check_url_allowed(url: str,
                      allow_domains: List[str],
                      include_urls: List[str],
                      exclude_urls: List[str]) -> bool:
    
    url_parse = urlparse(url)
    scheme = url_parse.scheme
    domain = url_parse.netloc
    path = url_parse.path
    query = url_parse.query
    url_no_scheme = f'{domain}{path}?{query}'

    domain_allowed = any(
        _check_pattern_with_wildcard(allow_domain, domain)
        for allow_domain in allow_domains
    )
    url_included = any(
        _check_pattern_with_wildcard(include_url, url_no_scheme)
        for include_url in include_urls
    )
    url_excluded = any(
        _check_pattern_with_wildcard(exclude_url, url_no_scheme)
        for exclude_url in exclude_urls
    )
    return domain_allowed and url_included and not url_excluded

def to_abs_url(base_url: str, path: str) -> str:
    try:
        abs_url = urljoin(base_url, path)
        return abs_url if abs_url.startswith('http') else ''
    except Exception as err:
        print(f'Error combining "{base_url}" and "{path}"')
    return ''

def url_to_origin(url: str) -> str:
    url_parse = urlparse(url)
    scheme = url_parse.scheme
    domain = url_parse.netloc
    return f'{scheme}://{domain}'

def remove_fragment(url: str) -> str:
    return url.split('#')[0]