import sys
import os
import random
from math import log2

from disjoint_set import DisjointSet

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler import GraphManager

def generate_fake_graph(n_html: int, n_resource: int, max_degree: int, avg_degree: int, output_path: str) -> GraphManager:
    id_to_url = lambda url_id: f'http://example.com/{hex(url_id)}'
    edges = []

    # Fulfill connectivity
    ds = DisjointSet(n_html)
    while len(ds) > 1:
        a = random.randint(0, n_html-1)
        b = random.randint(0, n_html-1)
        if not ds.same(a, b):
            ds.union(a, b)
            edges.append((min(a, b), max(a, b)))
    
    # Fulfill max_degree
    dests = random.sample(range(0, n_html), k=max_degree)
    for dest in dests: edges.append((0, dest))

    # Connect non-html-resources
    n_non_html = n_resource - n_html
    non_html_degrees = [
        random.randint(1, 3) + (round(n_html * 0.1) if (url_id - n_html) < log2(n_non_html) else 0)
        for url_id in range(n_html, n_resource)
    ]
    for url_id, degree in enumerate(non_html_degrees, n_html):
        srcs = random.sample(range(0, n_html), k=degree)
        for src in srcs: edges.append((src, url_id))

    # Fulfill avg_degree
    new_avg_degree = round((avg_degree * n_html - len(edges)) / n_html)
    degree_dis = min(new_avg_degree, 10)
    html_degrees = [random.randint(new_avg_degree - degree_dis, new_avg_degree + degree_dis) for _ in range(n_html)]
    for url_id, degree in enumerate(html_degrees):
        srcs = random.sample(range(0, n_html), k=degree)
        for src in srcs: edges.append((url_id, src))
    
    # Dump to graphmanager
    adjList = [[] for _ in range(n_html)]
    for src, dest in edges:
        adjList[src].append(dest)
    
    urls = [id_to_url(id) for id in range(n_resource)]
    gm = GraphManager()
    for src, dests in enumerate(adjList):
        gm._add_links(urls[src], [urls[dest] for dest in dests])

    gm.save_to_file(output_path)
    print(gm.get_statistic())

if __name__ == '__main__':
    if len(sys.argv) < 5: 
        print('Usage: fake_graph_generator.py <n_html> <n_resources> <max_degree> <avg_degree> [output_path]')
        exit(1)
    
    generate_fake_graph(
        int(sys.argv[1]),
        int(sys.argv[2]),
        int(sys.argv[3]),
        int(sys.argv[4]),
        sys.argv[5] if len(sys.argv) > 5 else 'output.pkl'
    )
