import igraph 
from wfqc.network import create_cocitation_graph, add_graph_attributes
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

    # Tools citing each other
    ('TC', 'TD'), 

    # Duplicate edges
    ('CE', 'TF'), ('CE', 'TF'),

    # Tools citing themselves
    ('TA', 'TA'),

    # Disconnected cluster
    ('CF', 'TE'), ('CF', 'TF')

]



cocitation_expected_nodes = ['TA', 'TC', 'TD', 'TE', 'TF']
citation_expected_nodes = ['TA', 'TC', 'TD', 'TE', 'TF', 'CC', 'CD', 'CF', ]
expected_edge_weights = {('TA', 'TC'): 2, ('TC', 'TD'): 1, ('TE', 'TF'): 1,
('TE', 'TG'): None, # G not in graph
('TA', 'TE'): 0} # both nodes in graph, but no connection

tool_metadata = {
    "tools": [
        {'name': 'ToolnameA', 'pmid': 'TA', 'nrCitations': 1, 'pubdate': 2015},
        {'name': 'ToolnameB', 'pmid': 'TB', 'nrCitations': 2, 'pubdate': 2016}, 
        {'name': 'ToolnameC', 'pmid': 'TC', 'nrCitations': 3, 'pubdate': 2017},
        {'name': 'ToolnameD', 'pmid': 'TD', 'nrCitations': 4, 'pubdate': 2018},
        {'name': 'ToolnameE', 'pmid': 'TE', 'nrCitations': 5, 'pubdate': 2019},
        {'name': 'ToolnameF', 'pmid': 'TF', 'nrCitations': 6, 'pubdate': 2020}
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
        "TC_02": "14632076",
        "TD_04": "29400476",
        "TA_01": "14976030",
        "TA_03": "14976030"
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


citation_graph = igraph.Graph.TupleList(edges, directed=True)
included_tools = [tool for tool in citation_graph.vs['name'] if tool in tools]  
cocitation_graph = create_cocitation_graph(citation_graph,included_tools)
cocitation_graph = add_graph_attributes(graph=cocitation_graph, metadata_file=tool_metadata)