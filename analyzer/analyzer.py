import dataclasses
from typing import List, Tuple

from crawler import GraphManager
from .config import AnalyzerConfig, AnalyzeAlgorithm
from .pagerank import PageRank

class Analyzer:
    def __init__(self,
                 graph_manager: GraphManager,
                 config: AnalyzerConfig) -> None:
        self.__config = dataclasses.replace(config)
        self.__graph_manager = graph_manager

    def main(self) -> List[Tuple[str, float]]:
        """
        Main method to start the analysis process.

        Returns:
            List[Tuple[str, float]]: List of tuples containing the URL and the
            corresponding weight.
        """
        pr = PageRank(self.__graph_manager,
                      self.__config.damping,
                      self.__config.convergence)

        if self.__config.algorithm == AnalyzeAlgorithm.PAGERANK_PY:
            url_and_weight = pr.pagerank_py()
            weight_max = url_and_weight[0][1]
            return [(url, weight / weight_max) for url, weight in url_and_weight]
        elif self.__config.algorithm == AnalyzeAlgorithm.PAGERANK_PYMAT:
            url_and_weight = pr.pagerank_pymat()
            weight_max = url_and_weight[0][1]
            return [(url, weight[0] / weight_max[0]) for url, weight in url_and_weight]
        elif self.__config.algorithm == AnalyzeAlgorithm.PAGERANK_NP:
            url_and_weight = pr.pagerank_np()
            weight_max = float(url_and_weight[0][1])
            return [(url, float(weight) / weight_max) for url, weight in url_and_weight]
        elif self.__config.algorithm == AnalyzeAlgorithm.PAGERANK_CUPY:
            url_and_weight = pr.pagerank_cupy()
            weight_max = float(url_and_weight[0][1])
            return [(url, float(weight) / weight_max) for url, weight in url_and_weight]
        else:
            raise NotImplementedError(f'Algorithm {self.__config.algorithm} not implemented')