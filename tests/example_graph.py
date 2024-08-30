import igraph 
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from pubmetric.network import create_cocitation_graph, add_graph_attributes
# Define the nodes 
tools = ['TA', 'TC', 'TD', # connected cluster - included in final graph 
        # Separate cluster - included in final graph 
         'TE', 'TF',
        # Single disconnected cited - not included in final graph 
         'TB']

citations = ['CA', 'CB', 'CC', 'CD', 'CE', 'CF', 'CG']

edges = [

    # Single citations of tools
    ('CA', 'TA'), ('CB', 'TB'),

    # Citations to multiple tools
    ('CC', 'TA'), ('CC', 'TC'),
    ('CD', 'TA'), ('CD', 'TC'),
    ('CE', 'TC'), ('CE', 'TD'),

    # Tools citing each other, excluded
    ('TC', 'TD'),

    # Duplicate edges, removed
    ('CX', 'TF'), ('CX', 'TF'),

    # Tools citing themselves
    ('TA', 'TA'),

    # Disconnected cluster
    ('CF', 'TE'), ('CF', 'TF')

]

paper_citations = {
    'CA':['TA'], 
    'CB':['TB'], 
    'CC':['TA', 'TC'], 
    'CD':['TA', 'TC'], 
    'CE': ['TC', 'TD'],
    'CF':['TE', 'TF'], 
}



cocitation_expected_nodes = ['TA', 'TC', 'TD', 'TE', 'TF']
citation_expected_nodes = ['TA', 'TC', 'TD', 'TE', 'TF', 'CC', 'CD', 'CF', ]
expected_edge_weights = {('TA', 'TC'): 2, ('TC', 'TD'): 1, ('TE', 'TF'): 1,
('TE', 'TG'): None, # G not in graph
('TA', 'TE'): 0} # both nodes in graph, but no connection

tool_metadata = {
    "tools": [
        {'name': 'ToolnameA', 'pmid': 'TA', 'nr_citations': 1, 'publication_date': 2015},
        {'name': 'ToolnameB', 'pmid': 'TB', 'nr_citations': 2, 'publication_date': 2016},
        {'name': 'ToolnameC', 'pmid': 'TC', 'nr_citations': 3, 'publication_date': 2017},
        {'name': 'ToolnameD', 'pmid': 'TD', 'nr_citations': 4, 'publication_date': 2018},
        {'name': 'ToolnameE', 'pmid': 'TE', 'nr_citations': 5, 'publication_date': 2019},
        {'name': 'ToolnameF', 'pmid': 'TF', 'nr_citations': 6, 'publication_date': 2020}
    ]
}

pmid_workflow = [('TA', 'TC'), ('TC', 'TD'), ('TA', 'TD')]

dictionary_workflow = {
    "edges": [
        [
            "TA_01",
            "TC_02"
        ],
        [
            "TC_02",
            "TD_04"
        ],
        [
            "TA_03",
            "TD_04"
        ]
    ],
    "steps": {
        "TC_02": "TC",
        "TD_04": "TD",
        "TA_01": "TA",
        "TA_03": "TA"
    },
    "pmid_edges": [
        [
            "TA",
            "TC"
        ],
        [
            "TC",
            "TD"
        ],
        [
            "TA",
            "TD"
        ]
    ]
}



cocitation_graph = create_cocitation_graph(paper_citations)
cocitation_graph = add_graph_attributes(graph=cocitation_graph, metadata_file=tool_metadata)