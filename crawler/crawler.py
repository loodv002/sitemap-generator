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

from typing import Dict, List, Set, Callable, Optional

from .config import CrawlerConfig
from .graph_manager import GraphManager
from .url_utils import *

class CrawlerTask:
    def __init__(self, method: str, url: str, callback: Callable):
        self.method = method
        self.url = url
        self.callback = callback

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
        self.__url_to_crawl: queue.Queue[CrawlerTask] = queue.Queue()
        self.__index_urls_set = set(self.__config.index_urls)
        for index_url in self.__config.index_urls:
            self.graph_manager.get_id_by_url(index_url)
            self.__url_to_crawl.put(CrawlerTask(
                method   = 'GET',
                url      = index_url,
                callback = self.__page_parse_handler
            ))

        # Variables that require lock protection.
        self.__all_crawl_finish = False
        self.__current_crawling_count = 0
        self.__url_check_created: Set[int] = set()

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
            get_new_tasks = False
            with self.__lock, contextlib.suppress(queue.Empty):
                task: CrawlerTask = self.__url_to_crawl.get_nowait()
                self.__current_crawling_count += 1
                get_new_tasks = True
                
            if not get_new_tasks:
                time.sleep(1)
                continue

            self.__log(f'Worker {worker_id} handling "{task.method}-{task.url}" start, pending tasks: {self.__url_to_crawl.qsize()}.')
    
            response = self.__request_with_retry(session, task.method, task.url)
            task.callback(task.url, response)

            self.__log(f'Worker {worker_id} handling "{task.method}-{task.url}" finish, pending tasks: {self.__url_to_crawl.qsize()}.')
            
            with self.__lock:
                self.__current_crawling_count -= 1

                if self.__current_crawling_count == 0 and self.__url_to_crawl.empty():
                    self.__all_crawl_finish = True

    def __page_parse_handler(self, url: str, response: Optional[requests.Response]):
        if not response: return False
        if response.status_code != 200: return False

        page_html = response.text
        links = self.__parse_page(url, page_html)

        self.graph_manager._add_links(url, links)
        url_ids = [self.graph_manager.get_id_by_url(link)
                   for link in links]

        with self.__lock:
            # Prevent same link in multiple threads obtain "url not checked" state.
            urls_to_check = [link
                             for link, url_id in zip(links, url_ids)
                             if url_id not in self.__url_check_created]
            self.__url_check_created.update(url_ids)
        
        for link in urls_to_check:
            if not self.__url_filter(link): continue

            self.__url_to_crawl.put(CrawlerTask(
                method   = 'HEAD',
                url      = link,
                callback = self.__url_check_handler
            ))

            self.__log(f'Add "HEAD-{link}" to queue, pending tasks: {self.__url_to_crawl.qsize()}.')

        return True

    def __url_check_handler(self, url: str, response: Optional[requests.Response]):
        if not response: return
        elif response.status_code != 200: return
        elif not response.headers.get('Content-Type', '').startswith('text/html'): return

        self.__url_to_crawl.put(CrawlerTask(
            method   = 'GET',
            url      = url,
            callback = self.__page_parse_handler
        ))
        
        self.__log(f'Add "GET-{url}" to queue, pending tasks: {self.__url_to_crawl.qsize()}.')

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
        links = [remove_fragment(link) for link in links if link]
        links = list(set(links))
        return links