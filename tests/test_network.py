import pytest
from WFQC import network as nw
import igraph

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


def test_cictations():
    G, included_tools = nw.create_citation_network(loadData=False, testSize=20) 
    assert len(G.vs['name']) == len(included_tools) # all the tools are still in the graph after transforming into edge cocitation graph.