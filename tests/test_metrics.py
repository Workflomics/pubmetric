
import pytest
from wfqc import network as nw
from wfqc.metrics import *
from wfqc.workflow import parse_cwl_workflows
from wfqc.network import create_citation_network

import igraph
import os
import math

from data.test_graph import cocitation_graph, tool_metadata, expected_edge_weights


def test_get_graph_edge_weight():
    for edge, expected_weight in expected_edge_weights.items():
        weight = get_graph_edge_weight(cocitation_graph, edge)
        assert weight == expected_weight
 

def test_workflow_level_average_sum():
    test_workflows = [ [('TA', 'TC'), ('TC', 'TD')],[('TA', 'TB')] ]
    expected_scores = [1.5, 0.0]    # obs see the problem here where this metrics prefers single edged nw with good connection (msConvert to Comet for ex will always be best then)
    for i, workflow in enumerate(test_workflows):
        assert workflow_average_sum(cocitation_graph, workflow) == expected_scores[i]

def test_invert_edges():
    print()

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