from dataclasses import dataclass
from enum import Enum

class AnalyzeAlgorithm(Enum):
    PAGERANK_PY = 'pagerank_py'
    '''PageRank algorithm in python. Serial Implementation.'''

    PAGERANK_NP = 'pagerank_np'
    '''PageRank algorithm in numpy. Serial Implementation.'''

    PAGERANK_CUPY = 'pagerank_cupy'
    '''PageRank algorithm in cupy. CUDA Implementation.'''

@dataclass
class AnalyzerConfig:
    damping: float = 0.85
    '''Damping factor for pagerank algorithm.'''

    convergence: float = 1e-7
    '''Convergence threshold for pagerank algorithm.'''

    algorithm: AnalyzeAlgorithm = AnalyzeAlgorithm.PAGERANK_PY