import networkx as nx

graph = nx.Graph()

def add_paper_to_graph(paper_data):
    title = paper_data["title"]
    graph.add_node(title, type="paper")

    graph.add_node("method", type="concept")
    graph.add_edge(title, "method")

    return graph
