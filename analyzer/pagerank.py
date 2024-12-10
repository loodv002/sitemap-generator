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
        weights = [[1/numNodes for _ in range(numNodes)], None]
        residule_factor = (1-self.__damping) / numNodes

        out_degrees = [len(self.__graphmanager.get_links_by_id(i)) for i in range(numNodes)]
        no_outgoing_weight_row = [int(out_degree == 0) for out_degree in out_degrees]
        no_outgoing_weight_array = list(map(lambda x: x/numNodes, no_outgoing_weight_row))

        non_zero_out_degrees = out_degrees.copy()
        non_zero_out_degrees = list(map(lambda x: x if x != 0 else 1, non_zero_out_degrees))

        rev_links = [self.__graphmanager.get_rev_links_by_id(i) for i in range(numNodes)]

        rev_weights_sum = [0 for _ in range(numNodes)]
        rev_weights = [0 for _ in range(numNodes)]

        step = 0
        while True:
            curStep = step % 2
            nextStep = (step + 1) % 2

            rev_weights = [x/y for x,y in zip(weights[curStep], non_zero_out_degrees)]
            for i, rev_link in enumerate(rev_links):
                rev_weights_sum[i] = sum(rev_weights[j] for j in rev_link)
            
            weights[nextStep] = [0 for _ in range(numNodes)]
            for i in range(numNodes):
                weights[nextStep][i] = sum([no_outgoing_weight_array[j] * w for j,w in enumerate(weights[curStep])]) + rev_weights_sum[i]
            weights[nextStep] = list(map(lambda x: self.__damping * x + residule_factor, weights[nextStep]))

            global_diff = sum([abs(weights[nextStep][i] - weights[curStep][i]) for i in range(numNodes)])
            if global_diff < self.__covergence:
                break
            step += 1

        return [(self.__graphmanager.get_url_by_id(i), weights[curStep][i]) for i in range(numNodes)]
    
    def pagerank_np(self) -> List[Tuple[str, float]]:
        numNodes = self.__graphmanager.get_url_count()
        weights = [np.zeros(numNodes, dtype=np.float32) + (1 / numNodes), None]
        residule_factor = (1-self.__damping) / numNodes

        out_degrees = np.array([len(self.__graphmanager.get_links_by_id(i)) for i in range(numNodes)], dtype=np.uint32)
        no_outgoing_weight_row = np.array([int(out_degree == 0) for out_degree in out_degrees])
        no_outgoing_weight_array = no_outgoing_weight_row.astype(np.float32) / numNodes

        non_zero_out_degrees = out_degrees.copy()
        non_zero_out_degrees[out_degrees == 0] = 1

        rev_links = [self.__graphmanager.get_rev_links_by_id(i) for i in range(numNodes)]

        rev_weights_sum = np.zeros(numNodes, dtype=np.float32)
        rev_weights = np.zeros(numNodes, dtype=np.float32)

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
        weights = [cp.zeros(numNodes, dtype=cp.float32) + (1 / numNodes), None]
        residule_factor = (1-self.__damping) / numNodes

        out_degrees = np.array([len(self.__graphmanager.get_links_by_id(i)) for i in range(numNodes)], dtype=np.uint32)
        no_outgoing_weight_row = np.array([int(out_degree == 0) for out_degree in out_degrees])
        no_outgoing_weight_array = no_outgoing_weight_row.astype(np.float32) / numNodes

        non_zero_out_degrees = out_degrees.copy()
        non_zero_out_degrees[out_degrees == 0] = 1

        rev_links = [self.__graphmanager.get_rev_links_by_id(i) for i in range(numNodes)]

        rev_weights_sum = np.zeros(numNodes, dtype=np.float32)
        rev_weights = np.zeros(numNodes, dtype=np.float32)

        step = 0
        while True:
            curStep = step % 2
            nextStep = (step + 1) % 2

            rev_weights = weights[curStep].get() / non_zero_out_degrees
            for i, rev_link in enumerate(rev_links):
                rev_weights_sum[i] = sum(rev_weights[j] for j in rev_link)

            weights[nextStep] = self.__damping * (
                cp.array(rev_weights_sum) + cp.array(no_outgoing_weight_array) @ cp.array(weights[curStep])
            ) + residule_factor
            
            global_diff = cp.sum(cp.abs(cp.subtract(weights[nextStep], weights[curStep])))
            if global_diff < self.__covergence:
                break
            step += 1
        
        return [(self.__graphmanager.get_url_by_id(i), weights[curStep][i]) for i in range(numNodes)]
