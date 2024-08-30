
import pickle
import os
import math
from datetime import datetime
import statistics

import example_graph as ex_graph

import pubmetric.metrics as met
from pubmetric.workflow import parse_cwl
from pubmetric.network import create_network

 
def test_tool_level_average_sum(shared_datadir):
    cwl_filename = os.path.join(shared_datadir, "candidate_workflow_repeated_tool.cwl")
    graph_path = os.path.join(shared_datadir, "graph.pkl")
    with open(graph_path, 'rb') as f:
        graph = pickle.load(f) 
    workflow = parse_cwl(graph=graph , cwl_filename=cwl_filename)
    # graph = asyncio.run(create_network(inpath=shared_datadir, test_size=20, load_graph=True))
    tool_scores = met.tool_average_sum(graph, workflow)
    assert list(tool_scores.keys()) == ['ProteinProphet_02', 'StPeter_04', 'XTandem_01', 'XTandem_03'] # note this only tests the format is right
    assert tool_scores['XTandem_01'] != tool_scores['XTandem_03']

# The rest of the tests are based on the example graph
def test_get_graph_edge_weight():
    id_dict = met.get_node_ids(ex_graph.cocitation_graph)
    print(ex_graph.cocitation_graph.vs['name'])
    for edge, expected_weight in ex_graph.expected_edge_weights.items():
        weight = met.get_graph_edge_weight(graph=ex_graph.cocitation_graph, edge=edge, id_dict=id_dict)
        assert weight == expected_weight

def test_workflow_average_base():
    # obs see the problem here where this metrics prefers single edged nw with good connection (msConvert to Comet for ex will always be best then)
    assert met.workflow_average(graph=ex_graph.cocitation_graph, workflow=ex_graph.pmid_workflow) == (2 + 1 + 0) / 3
    assert met.workflow_average(graph=ex_graph.cocitation_graph, workflow=[('TA', 'TB')] ) == 0/1 # not connected

def test_complete_average_base():
    score = met.complete_average(graph=ex_graph.cocitation_graph, workflow= ex_graph.dictionary_workflow)
    assert score == round(( 2 + 1 + 2/4 + 0 + 0 + 0 ) / 3, 2)

def test_sqrt_workflow_average_sum():
    sqrt_score = met.workflow_average(graph = ex_graph.cocitation_graph, workflow=ex_graph.pmid_workflow, transform='sqrt')
    assert sqrt_score == round(( math.sqrt(2) + math.sqrt(1) + math.sqrt(0) ) / 3, 2)

def test_log_workflow_average_sum():
    log_score = met.workflow_average(ex_graph.cocitation_graph, workflow=ex_graph.pmid_workflow, transform='log')
    assert log_score == round((math.log(2 + 1) + math.log(1 + 1) + math.log(0 + 1)) / 3, 2)

def test_degree_workflow_average_sum():
    assert met.workflow_average(graph=ex_graph.cocitation_graph, workflow=ex_graph.pmid_workflow, degree_adjustment=True) == round((2 / min(1, 2) + 1 / min(1, 2) + 0/1 ) / 3, 2)

def test_workflow_product_aggregation():
    assert met.workflow_average(graph=ex_graph.cocitation_graph, workflow=ex_graph.pmid_workflow, aggregation_method="product") == round(2*1/3, 2) # 0 values are not included

def test_log_product_aggregation():
    assert met.workflow_average(graph=ex_graph.cocitation_graph, workflow=ex_graph.pmid_workflow, aggregation_method="product", transform='log') == round(math.log(2+1) * math.log(1+1)/3, 2) # 0 values are not included

def test_workflow_average_sum_age():
    TA_age = datetime.now().year-2015
    TC_age = datetime.now().year-2017
    TD_age = datetime.now().year-2018
    score = met.workflow_average(graph=ex_graph.cocitation_graph, workflow=ex_graph.pmid_workflow, age_adjustment=True)
    print(score)
    assert score == round(( 2 / (min(TA_age, TC_age))  +  1 / (min(TC_age, TD_age)) ) / 3, 2)

def test_complete_average_age():
    TA_age = datetime.now().year-2015 # 9
    TC_age = datetime.now().year-2017 # 7
    TD_age = datetime.now().year-2018 # 6
    score = met.complete_average(ex_graph.cocitation_graph, workflow= ex_graph.dictionary_workflow, age_adjustment=True)
    assert score ==  round(( 2 / (min(TA_age, TC_age))  +  (2 / min(TA_age, TC_age) ) /4  + 1 / (min(TD_age, TC_age))  ) / 3, 2)

def test_citations():
    score = met.median_citations(ex_graph.cocitation_graph, workflow= ex_graph.dictionary_workflow)
    assert score == statistics.median([1, 1, 3, 4]) # TA is counted twice. Cant argue what is more or less reasonable as it is not a reasonable metric