import pytest
from wfqc import network as nw
import igraph
import numpy as np
import pickle

# def test_create_citation_network():
#     G, included_tools = nw.create_citation_network(loadData=False, testSize=10) # TODO: if no data then make data or ask if make data?
#     assert len (included_tools) > 0

def test_testsize_citation_network():
    G, included_tools = nw.create_citation_network(loadData=False, testSize=10) # TODO: if no data then make data or ask if make data?
    assert len (included_tools) > 0

def test_load_citation_network():
    G, included_tools = nw.create_citation_network(loadData=True) # TODO: if no data then make data or ask if make data?
    assert len (included_tools) > 0


def test_cocitation_graph():
    print('')


def test_cocitation(shared_datadir):

    with open(shared_datadir / "citation_path.pkl", 'rb') as f: # testgraph with problems
        citation_graph = pickle.load(f) 

    with open(shared_datadir / "cocitation_path.pkl", 'rb') as f: # testgraph with solved problems
        cocitation_graph = pickle.load(f) 

    tools = ['TA', 'TB', 'TC', 'TD', 'TE', 'TF', 'TG', 'TH']

    G = nw.cocitation_graph(citation_graph, tools)

    assert np.array_equal(np.sort(G.vs['name']), np.sort(cocitation_graph.vs['name']))