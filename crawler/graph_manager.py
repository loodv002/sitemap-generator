import threading
import pickle

from typing import List, Tuple, Dict, Set, NamedTuple, Any

class PipelineUpdate(NamedTuple):
    n_urls: int
    new_links: List[Tuple[int, int]]

class GraphManager:
    '''Record hyperlink graph.
    * Url are nodes in graph, represented by numeric id.
    * Hyperlink are directed edges in graph, represented by tuple (source node id, dest node id).
    '''
    
    def __init__(self):
        self.__lock = threading.Lock()

        self.__url_to_id: Dict[str, int] = {}
        '''Mapping between url and numeric id.'''
        self.__id_to_url: Dict[int, str] = {}
        '''Mapping between url id and url.'''
        
        self.__links_list: List[List[int]] = []
        '''Directed adjacency list of graph.'''
        self.__links_set: List[Set[int]] = []
        '''Directed adjacency list of graph, neighbors of each node are stored in a set.'''
        self.__rev_links_list: List[List[int]] = []
        '''Reversed adjacency list of graph.'''

        self.__all_links: List[Tuple[int, int]] = []
        '''Collection of all edges (i.e. hyperlink relations). \n
        An edge tuple (`a`, `b`) represent a hyperlink in page `url(a)` links to `url(b)`.'''

        self.__pipeline_all_links_from: int = 0
        '''Index of `self.__all_links`, represent where next pipeline update should start from.'''

        self.__is_html: Set[int] = set()
        '''Url id of html pages.'''

    def __getstate__(self):
        state = self.__dict__.copy()

        # Exclude self.__lock to pickle
        state.pop(f'_{self.__class__.__name__}__lock')

        return state
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__lock = threading.Lock()

    def _add_links(self, source_url: str, target_urls: List[str]):
        '''Add hyperlinks `target_urls` found in page `source_url`. \n
        Note: non-existing url nodes are created automatically.'''
        
        source_id = self.get_id_by_url(source_url)
        target_ids = [self.get_id_by_url(target_url) for target_url in target_urls]

        with self.__lock:
            self.__is_html.add(source_id)

            for target_id in target_ids:
                if target_id in self.__links_set[source_id]: continue

                self.__links_set[source_id].add(target_id)
                self.__links_list[source_id].append(target_id)
                self.__rev_links_list[target_id].append(source_id)
                self.__all_links.append((source_id, target_id))

    def url_exists(self, url: str) -> bool:
        '''Check if a url node exists.'''
        return url in self.__url_to_id
    
    def link_exists(self, source_id: int, target_id: int):
        '''Check hyperlink to `url(target_id)` exists in page `url(source_id)`'''
        return target_id in self.__links_set[source_id]

    def get_id_by_url(self, url: str) -> int:
        '''Get url id by url string. New id created automatically if url node not exists.'''
        if url in self.__url_to_id: 
            return self.__url_to_id[url]

        with self.__lock:
            id = len(self.__url_to_id)
            self.__url_to_id[url] = id
            self.__id_to_url[id] = url
            self.__links_set.append(set())
            self.__links_list.append(list())
            self.__rev_links_list.append(list())

        return id
    
    def get_url_by_id(self, id: int) -> str:
        '''Get url string by url id.'''
        return self.__id_to_url[id]
    
    def get_links_by_id(self, id: int) -> List[int]:
        '''Get all hyperlink url ids in page `url(id)`.'''
        return self.__links_list[id]
    
    def get_rev_links_by_id(self, id: int) -> List[int]:
        '''Get all referer url ids of `url(id)`.'''
        return self.__rev_links_list[id]
    
    def get_url_count(self) -> int:
        '''Get current number of url nodes.'''
        return len(self.__url_to_id)

    def pipeline_get_update(self) -> PipelineUpdate:
        '''Get graph modification since last call. \n
        **return** NamedTuple(
            n_urls: Current number of url nodes.
            new_links: A list of newly added hyperlinks.
        )'''
        with self.__lock:
            all_links_from = self.__pipeline_all_links_from
            self.__pipeline_all_links_from = len(self.__all_links)
            
            return PipelineUpdate(
                len(self.__url_to_id),
                self.__all_links[all_links_from:]
            )
        
    def save_to_file(self, output_file_name: str) -> None:
        with open(output_file_name, 'wb') as output_file:
            pickle.dump(self, output_file)

    @staticmethod
    def load_from_file(input_file_name: str) -> 'GraphManager':
        with open(input_file_name, 'rb') as input_file:
            return pickle.load(input_file)
        
    def get_statistic(self) -> Dict[str, Any]:
        with self.__lock:
            n_html_page = len(self.__is_html)
            n_resources = len(self.__url_to_id)
            n_links = len(self.__all_links)
            max_degree = max(len(link) for link in self.__links_list)
            avg_degree = sum(len(link) for link in self.__links_list) / n_html_page
        return {
            'n_html_page': n_html_page,
            'n_resources': n_resources,
            'n_links': n_links,
            'max_degree': max_degree,
            'avg_degree': avg_degree,
        }