"""Workflow parsing module"""
import os 

import pickle

import pubmetric.workflow as wf


def test_parse_cwl_workflow_repetition(shared_datadir):
    graph_path = os.path.join(shared_datadir, "graph.pkl") # do I have to load it every time?
    with open(graph_path, 'rb') as f:
        graph = pickle.load(f) 
    cwl_filename = os.path.join(shared_datadir, "candidate_workflow_repeated_tool.cwl")
    workflow = wf.parse_cwl(graph =graph, cwl_filename=cwl_filename)  
    
    assert workflow['edges'] == [('XTandem_01', 'ProteinProphet_02'), ('ProteinProphet_02', 'StPeter_04'), ('XTandem_03', 'StPeter_04')]

def test_parse_cwl_workflow_(shared_datadir):
    graph_path = os.path.join(shared_datadir, "graph.pkl") # do I have to load it every time?
    with open(graph_path, 'rb') as f:
        graph = pickle.load(f) 
    cwl_filename = os.path.join(shared_datadir, "candidate_workflow_test.cwl")
    workflow = wf.parse_cwl(graph =graph, cwl_filename=cwl_filename)  
    assert workflow['edges'] == [('XTandem_01', 'PeptideProphet_03'), ('XTandem_01', 'ProteinProphet_02'), ('ProteinProphet_02', 'StPeter_04'), ('PeptideProphet_03', 'StPeter_04')]
