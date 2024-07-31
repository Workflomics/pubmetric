"""
Bibliographic graph creation
"""
import os
from tqdm import tqdm       
import pickle
from datetime import datetime
import json
import aiohttp
import igraph 
import sys
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'src')))
import wfqc.data 




# TODO: now the default for topic_id is at the bottom of the fucntions calling it, I think it should be at the top. 
async def download_citation_data(outpath: str, topic_id: str, included_tools: list) -> tuple:
    """
    Runs all methods to download meta data for software tools in bio.tools; Downloads tools from specified domain, retrieves citations for PMIDs, 
    and generates co-citation network edges.

    :param outpath: Path to directory where output files should be saved.
    :param topic_id: The ID to which the downloaded tools belong, e.g., "Proteomics" or "DNA" as defined by EDAM ontology. 
    :param included_tools: A list of the pmids for the tools for which citations should be downloaded.

    :return: tuple
        A tuple containing edges (list) and citation data (dict).
    """
    # Get citations for each tool, and generate edges between them.

    edges = []
    citation_dict ={
        "topicID": topic_id,
        "tools" : []
    }

    for pmid in tqdm(included_tools, desc="Downloading citations from PMIDs"): 
        async with aiohttp.ClientSession() as session: 
            citations = await wfqc.data.europepmc_request(session, pmid) 
            for citation in citations:
                edges.append((citation, pmid)) # citations pointing to tools

            # TODO: Perhaps this should be removed when finalising package as it is inly used for stats. citationnr could be saved into the main metadatafile
            citation_dict['tools'].append({ 
                'pmid': pmid,
                'nrCitations': len(citations),
                'citations': citations
            })

    citation_filepath = outpath + '/' + f"citations.json" 
    with open(citation_filepath, 'w') as f:
        json.dump(citation_dict, f)
    
    return edges

def create_cocitation_graph(graph: igraph.Graph, vertices, inverted_weights: bool = False) -> igraph.Graph:
    """
    Generates a co-citation network graph from a given bipartite (though edges between given vertices can occur and are handeled) 
    graph and a list of vertices/nodes that will make up the CITED vertices. All other vertices are considered CITATIONS. 
    The intersection between first neighbours of a pair of CITED vertices (that is, the number of shared CITATIONS) are turned into 
    the edge weight of the edge between the pair. 
    Only pairs with a non-zero intersection have an edge between them in the co.citation graph.

    :param graph: igraph.Graph
        The original graph containing citation relationships.
    :param vertices: list
        List of vertices (nodes) in the graph for which co-citation relationships are to be analysed.
    :param inverted_weights: bool
        If True, invert weights to reflect distance instead of similarity.

    :return: igraph.Graph
        A co-citation network graph (CO_G) with edges representing co-citation relationships.
    """
    
    edges = [] # list of edges in new graph
    for i in range(len(vertices)):
        for j in range(i+1, len(vertices)):
            neighbors_of_first = set(graph.neighbors(vertices[i]))
            neighbors_of_second = set(graph.neighbors(vertices[j]))
            
            common_neighbors = neighbors_of_first.intersection(neighbors_of_second)
            weight = len(common_neighbors)


            # igraph crerates its own id, so getting back their og name to check if one of them cites the other. TODO: should these even be included? 
            original_neighbors_of_first = [graph.vs[id]['name'] for id in neighbors_of_first]
            original_neighbors_of_second = [graph.vs[id]['name'] for id in neighbors_of_second]

            if vertices[i] in original_neighbors_of_second or vertices[j] in original_neighbors_of_first: 
                weight += 1

            if weight> 0:
                if inverted_weights:
                    edges.append((vertices[i], vertices[j], (1 / weight) *100)) # append new edge and the weight, inverted to reflect closeness
                else:
                    edges.append((vertices[i], vertices[j], weight)) # append new edge and the weight, inverted to reflect closeness
    
    cocitation_graph = igraph.Graph.TupleList(edges, directed=False, weights=True)

    return cocitation_graph

def create_graph(edges: list, included_tools: list, cocitation: bool = True, workflow_length_threshold: int = 20) -> igraph.Graph:
    """
    Creates a bibliographic graph from a list of edges and ensures there are no self loops or multiples of edges.
    Removes disconnected nodes

    :param edges: List of edges (tuples) representing connections between nodes in the graph.
    :param tool_dictionary: Dictionary containing metadata about tools, including PMIDs.
    :param cocitation: Flag indicating whether to make the graph a cocitation graph or not.
    :param workflow_length_threshold: Integer representing the maximum number of tools cited by a single publication for it to be considered a workflow citation, rather than e.g. a review paper citing numerous tools.

    :return: Tuple containing:
        - graph: igraph.Graph object of the processed graph.
        - included_tools: List of PMIDs for tools included in the final graph.
        - node_degree_dict: Dictionary mapping node names to their respective degrees in the graph.
    """
     
    # Creating a directed graph
    raw_graph = igraph.Graph.TupleList(edges, directed=True)
    number_vertices_raw = len(raw_graph.vs)

    # Removing self citations (loops) and multiples of edges
    graph = raw_graph.simplify(multiple=True, loops=True, combine_edges=None)
    number_vertices_simple = len(graph.vs)
    print(f"Removed {number_vertices_raw - number_vertices_simple} self loops and multiples of edges.")

    # Removing disconnected vertices (that are not tools)
    vertices_to_remove = [v.index for v in graph.vs if v.degree() <= 1 and v['name'] not in included_tools]
    nr_removed_vertices = len(vertices_to_remove)
    graph.delete_vertices(vertices_to_remove)

    # Removing disconnected tools 
    vertices_to_remove = [v.index for v in graph.vs if v.degree() == 0]
    nr_removed_vertices += len(vertices_to_remove)
    graph.delete_vertices(vertices_to_remove)
    print(f"Removed {nr_removed_vertices} disconnected tools and citations (with degree less or equal to 1) in the 'bipartite' graph.")

    # Thresholding graph and removing non-tool nodes with node degrees greater than 20
    vertices_to_remove = [v for v in graph.vs if v.degree() > workflow_length_threshold and v['name'] not in included_tools]
    graph.delete_vertices(vertices_to_remove)
    print(f'Number of vertices removed with degree threshold {workflow_length_threshold}: {len(vertices_to_remove)}')

    # Updating included_tools to only contain lists that are in the graph  
    included_tools = [tool for tool in included_tools if tool in graph.vs['name']]


    # Convert graph to co-citation graph
    if cocitation:
        graph = create_cocitation_graph(graph, included_tools)
        print(f"Number of remaining tools/vertices is {len(graph.vs)}, and number of remaining edges are {len(graph.es)}")
        return graph
    else: 
        print(f"Number of remaining tools vertices is {len(included_tools)}, total number of vertices is {len(graph.vs)}")
        return graph # TODO: Included tools can be recreated outside using the metadatafile, check that this is not a problem

# WHY is optional not working here, not specifying default none is the entire reason for having is aaghh 
async def create_citation_network(outpath: Optional[str] = None, test_size: Optional[int] = None, topic_id: str = "topic_0121", random_seed: int = 42, load_graph: bool = False, inpath: str = '', save_files: bool = True) -> igraph.Graph:
    """
    Creates a citation network given a topic and returns a graph and the tools included in the graph.


    :param topic_id: str
        The ID to which the downloaded tools belong, e.g., "Proteomics" or "DNA" as defined by EDAM ontology. 
    :param test_size: int
        Determines the number of tools downloaded.
    :param random_seed: int, Specifies the seed used to randomly pick tools in a test run. Default is 42.
    :param load_graph: bool
        Determines if an already generated graph is loaded or if it is recreated. Needs the parameter inpath to be specified.  
    :param filepath: str
        Path to an already generated graph file.
    :param outpath: str
        Path to the output directory where newly generated graph files will be saved. If not provided,
        a timestamped directory will be created in the current working directory. TODO: make them all end up in a collective out dir
    :param inpath: str
        Path to an existing folder containing the metadata file and graph. Will be used to load them if possible.
    :param save_files: bool
        Determines if the newly generated graph is saved.

    :return: igraph.Graph
        The citation network graph created using igraph.


    """

    if load_graph: 
        if not inpath: 
            print('You need to provide a path to the graph you want to load')
            return  
            
        graph_path = f'{inpath}/graph.pkl'
        if os.path.isfile(graph_path): 
            with open(graph_path, 'rb') as f:
                graph = pickle.load(f) 
            print(f"Graph loaded from {inpath}")
        else:
            print(f"File not found. Please check that '{graph_path}' is the path to your graph and run again. Or set load_graph = False to create a new graph. ")
            return 
   
    else:
         # Create output folder
        if outpath: 
            os.mkdir(outpath) 
        else:
            if not os.path.isdir('outs'):
                os.mkdir('outs')
            outpath = f'outs/out_{datetime.now().strftime("%Y%m%d%H%M%S")}'
            os.mkdir(outpath)

        tool_metadata = await wfqc.data.get_tool_metadata(outpath=outpath, inpath=inpath, topic_id=topic_id, test_size=test_size, random_seed=random_seed)
        
        # Extract tool pmids which we use to greate the graph
        included_tools = list({tool['pmid'] for tool in tool_metadata['tools']})

        # Downloading data
        edges = await download_citation_data(outpath=outpath, topic_id=topic_id, included_tools=included_tools)
        # Creating the graph using igraph
        print("Creating citation graph using igraph.")

        graph =  create_graph(edges=edges, included_tools=included_tools)

        # Saving edges, graph and tools included in the graph 
        if save_files:
            print(f"Saving data to directory {outpath}.")  # TODO outs should be collected in singel out folder

            graph_path = os.path.join(outpath, 'graph.pkl') 

            with open(graph_path, 'wb') as f: #
                pickle.dump(graph, f)

    # returns a graph and the pmids of the tools included in the graph (tools connected by cocitations)
    return graph

