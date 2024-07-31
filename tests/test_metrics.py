
import pytest
from wfqc import network as nw
from wfqc.metrics import *
from wfqc.workflow import parse_cwl_workflows
from wfqc.network import create_citation_network

import igraph
import numpy as np
import json
import os
import asyncio
import shutil
import math

# The network

# Define the nodes 
tools = ['TA', 'TB', 'TC', 'TD', # connected cluster - included in final graph 
        # Separate cluster - included in final graph 
         'TE', 'TF',
        # Single disconnected cited - not included in final graph 
         'TG', 
        # Single disconnected not cited - not included in final graph 
         'TH']

citations = ['CA', 'CB', 'CC', 'CD', 'CE', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CL', 'CM', 'CN', 'CO', 'CP', 'CQ']


edges = [

    # Single citations of tools
    ('CA', 'TA'), ('CB', 'TB'), ('CC', 'TC'), ('CD', 'TD'), 
    ('CE', 'TE'), ('CF', 'TF'), ('CG', 'TG'),

    # Citations to multiple tools
    ('CJ', 'TA'), ('CJ', 'TB'),  
    ('CK', 'TA'), ('CK', 'TB'), ('CK', 'TC'),
    ('CL', 'TA'), ('CL', 'TB'), ('CL', 'TC'), ('CL', 'TD'), 
    
    # Duplicate edges
    ('CP', 'TE'), ('CP', 'TE'),

    # Tools citing each other
    ('TB', 'TC'), 

    # Tools citing themselves
    ('TA', 'TA'),

    # Disconnected cluster
    ('CQ', 'TE'), ('CQ', 'TF'), ('CO', 'TE'),
    ('CO', 'TF') 
]

nodes_in_final_network = ['TA', 'TB', 'TC', 'TD', 'TE', 'TF', 'CJ', 'CK', 'CL', 'CO', 'CQ' ]
tools_in_final_network = ['TA', 'TB', 'TC', 'TD', 'TE', 'TF']
expected_edge_weights = {('TA', 'TB'): 3, ('TA', 'TC'): 2, ('TA', 'TD'): 1,
('TB', 'TC'): 3, ('TB', 'TD'): 1,
('TC', 'TD'): 1, 
('TE', 'TF'): 2, 
('TE', 'TG'): None, # G not in graph
('TA', 'TE'): 0} # both nodes in graph, but no connection


testgraph = igraph.Graph.TupleList(edges, directed=True)
incuded_tools = [tool for tool in testgraph.vs['name'] if tool in tools] #could do interrsection    
test_coG = nw.create_cocitation_graph(testgraph,incuded_tools)



def test_get_node_ids():
    id_dict = get_node_ids(test_coG)
    
    assert test_coG.vs[id_dict['TA']].degree() == 3 # using id dict to get the degree of a node
    assert test_coG.vs[id_dict['TB']].degree() == 3 
    assert test_coG.vs[id_dict['TF']].degree() == 1 

def test_get_graph_edge_weight():
    for edge, expected_weight in expected_edge_weights.items():
        weight = get_graph_edge_weight(test_coG, edge)
        assert weight == expected_weight
 

def test_workflow_level_average_sum():
    test_workflows = [ [('TA', 'TC'), ('TC', 'TB'), ('TB', 'TD')],[('TA', 'TB')] ]
    expected_scores = [2, 3]    # obs see the problem here where this metrics prefers single edged nw with good connection (msConvert to Comet for ex will always be best then)
    for i, workflow in enumerate(test_workflows):
        assert workflow_level_average_sum(test_coG, workflow) == expected_scores[i]

def test_log_sum_metric():
    test_workflows = [ [('TA', 'TC'), ('TC', 'TB'), ('TB', 'TD')],[('TA', 'TB')] ]
    expected_scores = [sum([ math.log(ew) for ew in [2+1,3+1,1+1]] )/3 , math.log(3+1)]    # obs see the problem here where this metrics prefers single edged nw with good connection (msConvert to Comet for ex will always be best then)
    for i, workflow in enumerate(test_workflows):
        assert log_sum_metric(test_coG, workflow) == expected_scores[i]

def test_degree_norm_sum_metric():
    test_workflows = [ [('TA', 'TC'), ('TC', 'TB'), ('TB', 'TD')],[('TA', 'TB')] ]
    expected_scores = [2/3, 1]    # obs see the problem here where this metrics prefers single edged nw with good connection (msConvert to Comet for ex will always be best then)
    for i, workflow in enumerate(test_workflows):
        assert degree_norm_sum_metric(test_coG, workflow) == expected_scores[i]

def test_prod_metric():
    test_workflows = [ [('TA', 'TC'), ('TC', 'TB'), ('TB', 'TD')],[('TA', 'TB')] ]
    expected_scores = [2, 3]    # obs see the problem here where this metrics prefers single edged nw with good connection (msConvert to Comet for ex will always be best then)
    for i, workflow in enumerate(test_workflows):
        assert prod_metric(test_coG, workflow) == expected_scores[i]

def test_logprod_metric():
    test_workflows = [ [('TA', 'TC'), ('TC', 'TB'), ('TB', 'TD')],[('TA', 'TB')] ]
    expected_scores = [(math.log(3+1)*math.log(2+1)*math.log(1+1)/3), math.log(3+1)]    # obs see the problem here where this metrics prefers single edged nw with good connection (msConvert to Comet for ex will always be best then)
    for i, workflow in enumerate(test_workflows):
        assert logprod_metric(test_coG, workflow) == round(expected_scores[i], 3)

def test_complete_tree():
    assert complete_tree(test_coG, [('TA', 'TB'), ('TA', 'TC'), ('TA', 'TD')], normalise=True) == 2.75
    assert complete_tree(test_coG, [('TA', 'TB'), ('TA', 'TC'), ('TA', 'TD')], normalise=False) == 11


def test_tool_level_average_sum(shared_datadir):
    cwl_filename = os.path.join(shared_datadir, "candidate_workflow_repeated_tool.cwl")
    metadata_filename = os.path.join(shared_datadir, "tool_metadata_test20_topic_0121_20250705.json")

    workflow = parse_cwl_workflows(cwl_filename,metadata_filename )  
    graph = create_citation_network(inpath=shared_datadir)

    tool_scores = tool_level_average_sum(graph, workflow)
    assert list(tool_scores.keys()) == ['ProteinProphet_02', 'StPeter_04', 'XTandem_01', 'XTandem_03'] # note this only tests the format is right 