from typing import List, Tuple

from crawler import GraphManager

class PageRank:
    def __init__(self,
                 graphmanager: GraphManager,
                 damping: float,
                 convergence: float) -> None:
        self.__graphmanager = graphmanager
        self.__damping = damping
        self.__covergence = convergence

    def pagerank_py(self) -> List[Tuple[str, float]]:
        numNodes = self.__graphmanager.get_url_count()
        weights = [1/numNodes for _ in range(numNodes)]
        weights_new = [0 for _ in range(numNodes)]
        
        while True:
            no_outgoing_weight = 0.0

            for i in range(numNodes):
                no_outgoing_weight += (len(self.__graphmanager.get_links_by_id(i)) == 0) * self.__damping * weights[i] / numNodes
            for i in range(numNodes):
                weights_new[i] = 0.0
                for j in self.__graphmanager.get_rev_links_by_id(i):
                    weights_new[i] += weights[j] / len(self.__graphmanager.get_links_by_id(j))
                weights_new[i] = (self.__damping * weights_new[i]) + (1.0 - self.__damping) / numNodes
                weights_new[i] += no_outgoing_weight
            
            global_diff = sum([abs(weights_new[i] - weights[i]) for i in range(numNodes)])
            weights = weights_new.copy()
            if global_diff < self.__covergence:
                break
        
        return [(self.__graphmanager.get_url_by_id(i), weights[i]) for i in range(numNodes)]