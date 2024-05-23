import pytest
from WFQC import network as nw

def test_create_citation_network():
    G, included_tools = nw.create_citation_network(loadData=False, testSize=10) # TODO: if no data then make data or ask if make data?
    assert len (included_tools) > 0



