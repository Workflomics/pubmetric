"""
Graph creation
"""
import os
from tqdm import tqdm       
import pickle
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

import asyncio              # -"-
import nest_asyncio         # For jupyter asyncio compatibility 
nest_asyncio.apply()        # Automatically takes into account how jupyter handles running event loops
import jsonpath_ng as jp


# TODO: import jsonpath_ng.ext      # More efficient json processing look into if actually computationally more efficient 
import igraph               # Used to create te citationa graph 


import toolcitation.fetchtools


def create_citation_network(topicID="topic_0121", testSize=None, randomSeed=42, loadData=True, filePath='', outpath = None, inpath = '', saveFiles=True): # TODO: I just threw  code into this function- improve
    
    """
    Creates a citation network given a topic and returns a graph and the tools included in the graph

        
    Parameters
    ----------
    topicID : str, default "topic_0121" (proteomics) TODO: int? 
        The ID to which the tools belongs to, ex. "Proteomics" or "DNA" as defined by 
        EDAM ontology (visualisation: https://edamontology.github.io/edam-browser/#topic_0003)

    testSize : int or None, default None
        Determines the number of tools included in the citation graph.

    randomSeed : int, default 42
        Specifies what seed is used to randomly pick tools in a test run. 
    
    loadData : Boolean, default True
        Determines if already generated graph is loaded or if it is recreated.
    
    filePath : str  TODO: add filepath 
        Path to already generated graph

    saveFiles : Boolean, default True
        Determines if newly generated graph is saved. 

    """
   
        

    # Retrieve the data 
    # run the asynchronous function for single session requests 
    result = asyncio.run(toolcitation.fetchtools.get_biotools_metadata(topicID=topicID)) 
    pmids = result['pmid'].tolist() # should I use numpy for all my lists? 

    # Randomly picks out a subset of the pmids
    if testSize: 
        if not loadData:  
            print(f"Creating test-cocitation network of size {testSize}. Random seed is {randomSeed}.")
        np.random.seed(randomSeed)
        pmids = np.random.choice(pmids,testSize)
    else:
        testSize = '' # temp for the creation of files, so they dotn ahve none in name 
    
    # Edge creation 
    # Load previously created data or recreate it

    if loadData: # TODO: pickle maybe is not the way to go in future? 
        edge_path = f'{inpath}/edges{testSize}.pkl'
        graph_path = f'{inpath}/graph{testSize}.pkl'
        tool_path = f'{inpath}/tools{testSize}.pkl'
        
        if os.path.isfile(edge_path) and os.path.isfile(graph_path) and os.path.isfile(tool_path): # should give option to specify these names
            print("Loading saved graph.")
            with open(edge_path, 'rb') as f:
                unq_edges = pickle.load(f) # should be unique ones right 
            with open(graph_path, 'rb') as f:
                G = pickle.load(f) 
            with open(tool_path, 'rb') as f:
                included_tools = pickle.load(f) 
        else:
            print(f"Files not found. Please check that '{edge_path}', '{graph_path}' and '{tool_path}' are in your current directory and run again. Or set loadData = False, to create the files. ")
            return 
   
    else:
         # Create output folder
        if outpath: 
            os.mkdir(outpath) 
        else:
            outpath =  f'out_{datetime.now().strftime("%Y%m%d%H%M")}'
            os.mkdir(outpath)

        # edge creation using europepmc
        print("Downloading citation data from Europepmc.")
        
        # Creates a list of the tools that actually have citations, otherwise they are not included in the graph. 
        included_tools = []  
        edges = []

        # Get citations for each tool, and generate edges between them. 
        for pmid in tqdm(pmids, desc="Processing PMIDs"): 
            pmid = str(pmid) # EuropePMC requires str            
    
            citations = toolcitation.fetchtools.europepmc(pmid, page_size=1000)
            for citation in citations:
                edges.append((pmid, str(citation['id']))) # TODO: this is the wring way around? shoudl be citation to pmid, no? 
                if pmid not in included_tools:
                    included_tools.append(pmid) 
        
        print("Creating citation graph using igraph.")
        
        # Finding unique edges by converting list to a set (because tuples are hashable) and back to list.
        # TODO: better way?
        unq_edges =  list(set(edges)) 
        print(f"{len(unq_edges)} unique out of {len(edges)} edges total!")

        # Creating a directed graph with unique edges
        G = igraph.Graph.TupleList(unq_edges, directed=True)

        # Removing disconnected vertices (that are not tools) that do not have information value for the (current) metric
        # TODO: improve edge removal?
        print("Removing citations with degree less or equal to 1 (Non co-citations).")
        vertices_to_remove = [v.index for v in G.vs if v.degree() <= 1 and v['name'] not in included_tools] 
        G.delete_vertices(vertices_to_remove)
        vertices_to_remove = [v.index for v in G.vs if v.degree() == 0 ] # second run to remove the copletely detatched ones after first run sicne they wont give info anyways. 
        G.delete_vertices(vertices_to_remove) # This will remove isolated tools as well 

        # Updating included_tools to only contain lists that are in the graph  
        included_tools = [tool for tool in included_tools if tool in G.vs['name']] 


        # Saving edges, graph and tools included in the graph 


        if saveFiles:
            edge_path = f'{outpath}/edges{testSize}.pkl'
            graph_path = f'{outpath}/graph{testSize}.pkl'
            tool_path = f'{outpath}/tools{testSize}.pkl'

            print(f"Saving data to '{edge_path}', '{graph_path}' and '{tool_path}'.") # sould make these filenames dynamic
            # and save them 
            #Do this nicer later? 
            with open(edge_path, 'wb') as f:
                pickle.dump(unq_edges, f)

            with open(graph_path, 'wb') as f:
                pickle.dump(G, f)

            with open(tool_path, 'wb') as f:
                pickle.dump(included_tools, f)    

    # returns a graph and the pmids of the tools included in the graph (tools connected by cocitations)
    return G, included_tools 
