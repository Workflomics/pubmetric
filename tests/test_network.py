import asyncio
from wfqc.network import * 

from data.test_graph import citation_graph, edges, tools, cocitation_expected_nodes, citation_expected_nodes, included_tools, cocitation_graph


def test_test_size_citation_network(shared_datadir): 
    graph = asyncio.run(create_citation_network(load_graph=False, test_size=20, inpath=shared_datadir))
    assert len(graph.vs['name']) > 0 

def test_load_citation_network(shared_datadir):
    graph = asyncio.run(create_citation_network(load_graph=True, inpath = shared_datadir)) 
    assert len(graph.vs['name']) == 1219

def test_create_cocitation_graph():
    incuded_tools = [tool for tool in citation_graph.vs['name'] if tool in tools]    
    graph = create_cocitation_graph(citation_graph, incuded_tools)
    assert sorted(cocitation_expected_nodes) == sorted(graph.vs['name'])

def test_create_graph():
    graph = create_graph(edges, included_tools , cocitation=False)
    print(sorted(citation_expected_nodes) , sorted(graph.vs['name']))
    assert sorted(citation_expected_nodes) == sorted(graph.vs['name'])

def test_get_citation_data():
    tools = ['14632076'] # Protein prophet. 
    edges = asyncio.run(get_citation_data(tools))
    assert len(edges) >= 2900 # it has a lot of citations, 2965 currently (august 2024)

def test_invert_graph_weights():
    inverted_graph = add_inverted_edge_weights(cocitation_graph)
    assert sorted(inverted_graph.es['inverted_weight']) == sorted([0.5, 1.0, 1.0])
    assert inverted_graph.es.attributes() == ['weight', 'inverted_weight']

