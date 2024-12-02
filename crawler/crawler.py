import requests
import re
import threading
import dataclasses
import queue
import contextlib
import time
from datetime import datetime
from functools import partial
from enum import Enum, unique

from typing import Dict, Optional, List

from .config import CrawlerConfig
from .graph_manager import GraphManager
from .url_utils import *

class Crawler:
    def __init__(self, 
                 config: CrawlerConfig,
                 graph_manager: GraphManager = None) -> None:
        
        self.__config: CrawlerConfig = dataclasses.replace(config)
        self.graph_manager = graph_manager or GraphManager()
        
        self.__lock = threading.Lock()

        self.__url_filter = partial(
            check_url_allowed, 
            allow_domains = config.allow_domains,
            include_urls = config.include_urls,
            exclude_urls = config.exclude_urls,
        )

        self.__EXP_DELAY = [2 ** i for i in range(self.__config.n_retries)] + [0]
    
        # Init index urls.
        self.__url_to_crawl = queue.Queue()
        self.__index_urls_set = set(self.__config.index_urls)
        for index_url in self.__config.index_urls:
            self.graph_manager.get_id_by_url(index_url)
            self.__url_to_crawl.put(index_url)

        # Variables that require lock protection.
        self.__all_crawl_finish = False
        self.__current_crawling_count = 0

        # Init threads
        self.__threads = [
            threading.Thread(target=self.__worker, 
                             args=(worker_id,),
                             daemon=True)
            for worker_id in range(self.__config.n_threads)
        ]

    def main(self) -> None:
        [thread.start() for thread in self.__threads]
        [thread.join() for thread in self.__threads]

    def __log(self, messages):
        time_string = datetime.now().strftime("%H:%M:%S")
        log = f'[{time_string}] {messages}\n'
        
        print(log, end='')

    def __worker(self, worker_id: int) -> None:
        session = self.__get_session(worker_id)
        while not self.__all_crawl_finish:
            get_new_jobs = False
            with self.__lock, contextlib.suppress(queue.Empty):
                url = self.__url_to_crawl.get_nowait()
                self.__current_crawling_count += 1
                get_new_jobs = True
                
            if not get_new_jobs:
                time.sleep(1)
                continue

            self.__log(f'Worker {worker_id} handling "{url}" start.')
            self.__job_handler(session, url)
            self.__log(f'Worker {worker_id} handling "{url}" finish.')
            
            with self.__lock:
                self.__current_crawling_count -= 1

                if self.__current_crawling_count == 0 and self.__url_to_crawl.empty():
                    self.__all_crawl_finish = True

    def __job_handler(self, session: requests.Session, url: str) -> bool:
        response = self.__request_with_retry(session, 'GET', url)
        if not response: return False
        if response.status_code != 200: return False

        page_html = response.text
        links = self.__parse_page(url, page_html)

        with self.__lock:
            # Prevent same link in multiple threads obtain "url not exist" state.
            links_exist = [self.graph_manager.url_exists(link)
                        for link in links]

            self.graph_manager._add_links(url, links)
        
        for link, link_exist in zip(links, links_exist):
            if not link_exist and self.__check_new_url(session, link):
                self.__url_to_crawl.put(link)

                self.__log(f'Add "{link}" to queue.')

        return True

    def __get_session(self, worker_id: int) -> requests.Session:
        if self.__config.proxies:
            proxy = self.__config.proxies[worker_id % len(self.__config.proxies)]
        else:
            proxy = ''

        session = requests.Session()

        if proxy:
            session.proxies.update({
                'http': proxy,
                'https': proxy,
            })
        
        if self.__config.user_agent:
            session.headers.update({
                'User-Agent': self.__config.user_agent
            })

        for cookie_name, cookie_domain, cookie_value in self.__config.cookies:
            session.cookies.set(cookie_name,
                                cookie_value, 
                                domain=cookie_domain)

        session.verify = self.__config.verify
        
        return session

    def __get_referer(self, url: str) -> str:
        if url in self.__index_urls_set: return url

        url_id = self.graph_manager.get_id_by_url(url)
        referer_id = self.graph_manager.get_rev_links_by_id(url_id)[0]
        
        return self.graph_manager.get_url_by_id(referer_id)

    def __request_with_retry(self, 
                             session: requests.Session, 
                             http_method_name: str, 
                             url: str) -> Optional[requests.Response]:
        
        time.sleep(self.__config.per_thread_request_gap)
        referer = self.__get_referer(url)
        headers = {}
        headers['Referer'] = referer
        if url_to_origin(url) != url_to_origin(referer):
            headers['Origin'] = url_to_origin(referer)

        for retry_delay in self.__EXP_DELAY:
            try:
                return session.request(
                    http_method_name, 
                    url = url,
                    headers = headers,
                    timeout = self.__config.timeout,
                )
            except requests.exceptions.Timeout:
                self.__log(f'Request "{url}" timout.')
            except Exception as err:
                self.__log(f'Request "{url}" error: "{err}".')
            time.sleep(retry_delay)

        return None
    
    def __parse_page(self, url: str, page_html: str) -> List[str]:
        links = (
            re.findall(
                'href="((?:http:|https:|)[^":]+)"', 
                page_html
            ) + 
            re.findall(
                "href='((?:http:|https:|)[^':]+)'", 
                page_html
            )
        )
        links = [
            to_abs_url(url, link)
            for link in links
        ]
        links = [link for link in links if link]
        return links
    
    def __check_new_url(self, session: requests.Session, url: str) -> bool:
        if not self.__url_filter(url): return False

        response = self.__request_with_retry(session, 'HEAD', url)
        if not response or response.status_code != 200: return False
        return response.headers.get('Content-Type', '').startswith('text/html')