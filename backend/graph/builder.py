import networkx as nx
import json
from networkx.readwrite import json_graph

def build_research_graph(parsed_papers: list[dict]):
    """
    Construct a relational knowledge graph from parsed papers and their structured entities.
    """
    G = nx.Graph()
    
    # Root Category
    G.add_node("Research Domain", type="Root", size=30, label="Research Domain")

    for paper in parsed_papers:
        title = paper["title"]
        short_title = title[:30] + "..." if len(title) > 30 else title
        
        # Add Paper Node
        G.add_node(title, label=short_title, type="Paper", size=20)
        G.add_edge("Research Domain", title, relation="contains")
        
        # Extract structured data from Parser Agent
        struct = paper.get("structured_data", {})
        
        # Add Methodologies
        for method in struct.get("methodologies", []):
            if method and method != "Unknown":
                G.add_node(method, type="Method", size=15, label=method)
                G.add_edge(title, method, relation="uses")
                
        # Add Datasets
        for dataset in struct.get("datasets", []):
            if dataset and dataset != "Unknown":
                G.add_node(dataset, type="Dataset", size=15, label=dataset)
                G.add_edge(title, dataset, relation="evaluates_on")

        # Add Contributions
        for contrib in struct.get("contributions", []):
            if contrib and contrib != "Unknown":
                label = contrib[:20] + "..." if len(contrib) > 20 else contrib
                G.add_node(contrib, type="Contribution", size=10, label=label)
                G.add_edge(title, contrib, relation="contributes")

    return G

def graph_to_json(G):
    """
    Convert NetworkX graph to a format Streamlit/D3 can understand.
    """
    return json_graph.node_link_data(G)
