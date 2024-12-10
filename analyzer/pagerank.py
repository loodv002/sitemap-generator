from typing import List, Tuple
import numpy as np
import cupy as cp

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
    
    def pagerank_pymat(self) -> List[Tuple[str, float]]:
        numNodes = self.__graphmanager.get_url_count()
        weights = [[1/numNodes] for _ in range(numNodes)]
        residule_factor = [[(1-self.__damping) / numNodes] for _ in range(numNodes)]

        while True:
            no_outgoing_weight_row = [0 for _ in range(numNodes)]
            adjacency_matrix = [[0 for _ in range(numNodes)] for _ in range(numNodes)]
            for i in range(numNodes):
                no_outgoing_weight_row[i] = (len(self.__graphmanager.get_links_by_id(i)) == 0) / numNodes
                for j in self.__graphmanager.get_rev_links_by_id(i):
                    adjacency_matrix[i][j] = 1 / len(self.__graphmanager.get_links_by_id(j))
            
            no_outgoing_weight_array = [no_outgoing_weight_row.copy() for _ in range(numNodes)]
            weight_new = [[0] for _ in range(numNodes)]
            tmp = adjacency_matrix.copy()
            for i in range(numNodes):
                for j in range(numNodes):
                    tmp[i][j] += no_outgoing_weight_array[i][j]
            for i in range(numNodes):
                weight_new[i][0] = self.__damping * sum([tmp[i][j] * weights[j][0] for j in range(numNodes)]) + residule_factor[i][0]
            global_diff = sum([abs(weight_new[i][0] - weights[i][0]) for i in range(numNodes)])
            weights = weight_new.copy()
            if global_diff < self.__covergence:
                break
        return [(self.__graphmanager.get_url_by_id(i), weights[i]) for i in range(numNodes)]
    
    def pagerank_np(self) -> List[Tuple[str, float]]:
        numNodes = self.__graphmanager.get_url_count()
        weights = [np.zeros(numNodes, dtype=np.double) + (1 / numNodes), None]
        residule_factor = (1-self.__damping) / numNodes

        out_degrees = np.array([len(self.__graphmanager.get_links_by_id(i)) for i in range(numNodes)], dtype=np.uint32)
        no_outgoing_weight_row = np.array([int(out_degree == 0) for out_degree in out_degrees])
        no_outgoing_weight_array = no_outgoing_weight_row.astype(np.double) / numNodes

        non_zero_out_degrees = out_degrees.copy()
        non_zero_out_degrees[out_degrees == 0] = 1

        rev_links = [self.__graphmanager.get_rev_links_by_id(i) for i in range(numNodes)]

        rev_weights_sum = np.zeros(numNodes, dtype=np.double)
        rev_weights = np.zeros(numNodes, dtype=np.double)

        step = 0
        while True:
            curStep = step % 2
            nextStep = (step + 1) % 2

            rev_weights = weights[curStep] / non_zero_out_degrees
            for i, rev_link in enumerate(rev_links):
                rev_weights_sum[i] = sum(rev_weights[j] for j in rev_link)

            weights[nextStep] = self.__damping * (
                rev_weights_sum + no_outgoing_weight_array @ weights[curStep]
            ) + residule_factor
            
            global_diff = np.sum(np.abs(np.subtract(weights[nextStep], weights[curStep])))
            if global_diff < self.__covergence:
                break
            step += 1

        return [(self.__graphmanager.get_url_by_id(i), weights[curStep][i]) for i in range(numNodes)]
    
    def pagerank_cupy(self) -> List[Tuple[str, float]]:
        numNodes = self.__graphmanager.get_url_count()
        weights = cp.array([[1/numNodes] for _ in range(numNodes)], dtype=cp.double)
        residule_factor = cp.array([[(1-self.__damping) / numNodes] for _ in range(numNodes)], dtype=cp.double)

        while True:
            no_outgoing_weight_row = [0 for _ in range(numNodes)]
            adjacency_matrix = cp.zeros((numNodes, numNodes), dtype=np.double)
            for i in range(numNodes):
                no_outgoing_weight_row[i] = (len(self.__graphmanager.get_links_by_id(i)) == 0) / numNodes
                for j in self.__graphmanager.get_rev_links_by_id(i):
                    adjacency_matrix[i][j] = 1 / len(self.__graphmanager.get_links_by_id(j))
            
            no_outgoing_weight_array = cp.array([no_outgoing_weight_row for _ in range(numNodes)])
            weight_new = self.__damping * cp.matmul(cp.add(adjacency_matrix, no_outgoing_weight_array), weights) + residule_factor
            global_diff = cp.sum(cp.abs(cp.subtract(weight_new, weights)))
            weights = weight_new.copy()
            if global_diff < self.__covergence:
                break
        return [(self.__graphmanager.get_url_by_id(i), weights[i]) for i in range(numNodes)]
