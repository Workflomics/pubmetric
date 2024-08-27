import math
import statistics
from typing import Union, Optional

import numpy as np
import igraph


#TODO: all metrics that need to think about  workflow structure need to be updated to work with the new workflow representation 
# for ex: compelte tree needs to take into account the repeated tool several times


# General functions for interation with graph 

def get_node_ids(graph: igraph.Graph, key:str= "pmid") -> dict:
    """"
    Maps node names to their igraph IDs.

    :param graph: igraph.Graph 
    :param key: String indicating which of ID and name shoudl be used as key in the mapping dictionary

    :return: Dictionary mapping names to igraph IDs

    :raises ValueError: if the key is not either name or index 
    """
    if key == 'pmid':
        return {v['pmid']:v.index for v in graph.vs}
    elif key == 'name':
        return {v['name']:v.index for v in graph.vs}
    elif key == 'index':
        return {v.index:v['pmid'] for v in graph.vs}
    else:
        raise ValueError("Not a valid key")


def get_graph_edge_weight(graph: igraph.Graph,
                        edge: tuple,
                        id_dict: dict,
                        key: str = 'pmid',
                        transform: Optional[str] = None,
                        age_adjustment: bool = False,
                        degree_adjustment: bool = False) -> Union[float, None]:
    """
    Retrieves and optionally adjusts the weight of an edge between a pair of nodes in a graph.

    :param graph: An igraph.Graph object representing the graph, with weighted edges.
    :param edge: A tuple containing the identifiers (e.g., node names or PMIDs) of the two nodes forming the edge.
    :param id_dict: A dictionary mapping node identifiers to their corresponding indices in the graph.
    :param key: A string specifying the attribute key used to identify nodes in the graph. Default is 'pmid'.
    :param transform: Optional string specifying a transformation to apply to the edge weight (e.g., "log" or "sqrt"). Default is None.
    :param age_adjustment: Boolean indicating whether to adjust the weight based on the age of the nodes. Default is False.
    :param degree_adjustment: Boolean indicating whether to adjust the weight based on the degree of the nodes. Default is False.
    
    :return: A float representing the (possibly adjusted and transformed) weight of the edge in the graph. 
             If the nodes do not exist in the graph, it returns None. If the edge does not exist in the graph it returns 0.0.
    """

    if edge[0] not in graph.vs[key] or edge[1] not in graph.vs[key]:
        return None # If either node is not in the graph, the weight is None
    try:
        source = edge[0]
        target = edge[1]
        weight = graph.es.find(_between=((id_dict[source],), (id_dict[target],)))['weight']
    except (KeyError, ValueError):
        weight = 0.0  # If nodes are in the graph but not connected, the weight of the edge between them is 0

    # Transform
    if transform:
        weight = transform_weight(weight=weight, transform = transform)
    
    # Adjust
    if age_adjustment:
        weight = age_adjust_weight(edge=edge, weight=weight, graph=graph)
    if degree_adjustment:
        weight = degree_adjust_weight(edge=edge, weight=weight, graph=graph, id_dict=id_dict)

    return float(weight)

# Tool level metric

def tool_average_sum(graph: igraph.Graph,
                     workflow: dict,
                     aggregation_method: str = "sum",
                     transform: Optional[str] = None,
                     age_adjustment: bool = False,
                     degree_adjustment: bool = False) -> float:
    """
    Calculates the sum (or average if normalised) of edge weights per tool within a workflow.

    :param graph: An igraph.Graph co-citation graph.
    :param workflow: Dictionary with data about the workflow. # TODO reference a certain schema used for this 
    

    :return: Dictionary of the tool level metric score for each step
    """
    steps = list(workflow['steps'].keys())
    edges = workflow['edges']

    if not edges: # If it is an empty workflow
        return {}
    if len(edges) == 1:
        return {steps[0]: 1, steps[1]:1} # TODO or if norm by worflow score do that here too

    id_dict = get_node_ids(graph)

    step_scores = {}
    for step in steps:
        score = []
        for edge in edges:
            if step in edge:
                pmid_source = next( pmid for step_id, pmid in workflow['steps'].items() if step_id == edge[0] )
                pmid_target = next( pmid for step_id, pmid in workflow['steps'].items() if step_id == edge[1] )
                edge = (pmid_source, pmid_target)
                weight = get_graph_edge_weight(
                            graph=graph,
                            edge=edge,
                            id_dict=id_dict,
                            transform=transform,
                            age_adjustment=age_adjustment,
                            degree_adjustment=degree_adjustment
                        ) or 0.0
                
                score.append(weight)
        if score:
            if aggregation_method == "sum":
                step_scores[step] = round(float(sum(score)/len(score)), 2)
            if aggregation_method == "product":
                nonzero_scores = [w for w in score if w!=0]  #only use nonzero weights
                if nonzero_scores:
                    step_scores[step] = round(float(np.prod(nonzero_scores) / len(score)), 2)
                return 0.0  # If there are no weights
        else:
            step_scores[step] = 0

    # TODO: potentially also normalise by the total worklfow score to 
    return step_scores

# Workflow level metrics
def shortest_path(graph: igraph.Graph, workflow: list, weighted: bool = True) -> dict:
    """
    Computes shortest paths between each pair of nodes that have an edge in the workflow.

    :param graph: An igraph.Graph co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param weighted: Boolean indicating whether to compute weighted shortest paths (True) or unweighted (False).

    :return: Dictionary where keys are node pairs and values are shortest path distances.
    """
    if not workflow:
        return 0 
    
    id_dict = get_node_ids(graph) 

    distances = []


    for edge in workflow:
        u, v = edge

        u_index = id_dict.get(u, None)
        v_index = id_dict.get(v, None)

        if not u_index or not v_index:
            distances.append(10)
            continue

        if weighted:
            path_length = graph.get_shortest_paths(u_index, to=v_index, weights=graph.es["inverted_weight"], output="epath") or 10
        else:
            path_length = graph.get_shortest_paths(u_index, to=v_index, output="epath") 
        distances.append(len(path_length[0]))

    avg_distance = sum(distances)/len(workflow)
    return 1/avg_distance if avg_distance != 0 else 0

def workflow_average(graph: igraph.Graph,
                     workflow: Union[list, dict],
                     aggregation_method: str = "sum",
                     transform: Optional[str] = None,
                     age_adjustment: bool = False,
                     degree_adjustment: bool = False) -> float:
    """
    Calculates the sum (or average if normalised) of edge weights within a workflow.

    :param graph: An igraph.Graph co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    

    :return: Float value of the average sum metric calculated on the edges of the workflow.
    """

    if not workflow: # if there are no edges
        return 0
    
    if isinstance(workflow, dict):
        workflow = workflow['pmid_edges']
    
    # Get a mapping to the igraph ids
    id_dict = get_node_ids(graph)

    aggregated_weight = []
    for edge in workflow:
        weight = get_graph_edge_weight(
                    graph=graph,
                    edge=edge,
                    id_dict=id_dict,
                    transform=transform,
                    age_adjustment=age_adjustment,
                    degree_adjustment=degree_adjustment
                ) or 0.0  
        aggregated_weight.append(weight)

    if aggregation_method == "sum":
        return round(float(sum(aggregated_weight)/len(workflow)), 2)
    if aggregation_method == "product":
        nonzero_weights = [w for w in aggregated_weight if w!=0]  #only use nonzero weights
        if nonzero_weights:
            score =  np.prod(nonzero_weights) / len(workflow) 
            return round(float(score), 2)
        return 0.0  # If there are no weights

def complete_average(graph: igraph.Graph,
                    workflow: Union[dict,list],
                    factor: int = 4,
                    aggregation_method: str = "sum",
                    transform: Optional[str] = None,
                    age_adjustment: bool = False,
                    degree_adjustment: bool = False) -> float:
    # obs the repeated workflows will have a disadvantage because there is no edge between them which defaults to 0. This must be adjusted for in the devision of edges! TODO
    """
    Calculates the sum of the edge weights between all possible pairs of tools in a workflow.
    Named after the degree of connectivity - how close it is to being a complete graph - though this is weighted.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: Dictionary representing the workflow. TODO reference schema
    
    :return: Float value 
    """

    if isinstance(workflow, dict):
        step_names = list(workflow['steps'].keys())
        edges = workflow['edges']
    elif isinstance(workflow, list):
        step_names = list(set(element for tup in workflow for element in tup))
        edges = workflow

    nr_steps = len(step_names)
    nr_edges = len(edges)
    if nr_edges <1: # if there is only one tool there can be no edges
        return 0.0
    workflow_graph =  igraph.Graph.TupleList(edges, directed=False, weights=False)
    workflow_id_dict = get_node_ids(workflow_graph, key='name')
    full_graph_id_dict = get_node_ids(graph)
    
    aggregated_weight = []
    for i in range( nr_steps ):
        for j in range(i + 1, nr_steps ):
            if isinstance(workflow, dict):
                edge = (workflow['steps'][step_names[i]], workflow['steps'][step_names[j]])
            else:
                edge = (step_names[i], step_names[j])
            weight = get_graph_edge_weight(
                graph=graph,
                edge=edge,
                id_dict=full_graph_id_dict,
                transform=transform,
                age_adjustment=age_adjustment,
                degree_adjustment=degree_adjustment
            ) or 0.0
            u_index = workflow_id_dict.get(step_names[i], None)
            v_index = workflow_id_dict.get(step_names[j], None)
            
            path = workflow_graph.get_shortest_paths(u_index, to=v_index, output="epath") or None # if there is none then sth is wrong
            path_length= len(path[0])
            normalised_weight = weight / factor**(float(path_length)-1) if path_length else 0
            aggregated_weight.append(normalised_weight)

    if aggregation_method == "sum":
        return round(float(sum(aggregated_weight)/nr_edges), 2)
    if aggregation_method == "product":
        nonzero_weights = [w for w in aggregated_weight if w!=0]  #only use nonzero weights
        if nonzero_weights:
            score =  np.prod(nonzero_weights) /nr_edges
            return round(float(score), 2)
        return 0.0  # If there are no weights

def transform_weight(weight: int, transform: str) -> float:
    """
    Applies a mathematical transformation to the given weight.

    :param weight: Integer value representing the weight to be transformed.
    :param transform: String specifying the transformation to apply. 
                      Options include "log" for logarithmic transformation and "sqrt" for square root transformation.
    :return: Transformed weight as a float.
    """
    if transform == "log":
        return math.log(weight + 1)  # Log of weight + 1 to avoid -inf
        
    elif transform == "sqrt":
        return math.sqrt(weight)

def degree_adjust_weight(edge: tuple, weight, graph: igraph.Graph, id_dict: dict) -> float:
    """
    Adjusts the weight of an edge based on the average degree of its connected nodes.

    :param edge: Tuple representing the edge (source, target).
    :param weight: Float value of the initial weight of the edge.
    :param graph: An igraph.Graph object representing the graph.
    :param id_dict: Dictionary mapping node identifiers to their indices in the graph.
    :return: Weight adjusted by the average degree of the connected nodes.
    """
    source_degree = graph.vs[id_dict[edge[0]]].degree()
    target_degree = graph.vs[id_dict[edge[1]]].degree()

    min_degree = max(1, min([source_degree, target_degree]))
    return weight / min_degree

def age_adjust_weight(edge: tuple, weight, graph: igraph.Graph, default_age = 10, key: str = 'pmid') -> float:
    """
    Adjusts the weight of an edge based on the age of its connected nodes.

    :param edge: Tuple representing the edge (source, target).
    :param weight: Float value of the initial weight of the edge.
    :param graph: An igraph.Graph object representing the graph.
    :param default_age: Integer value representing the default age to use if node age is not found. Default is 10.
    :param key: String specifying the attribute key to look up node age in the graph. Default is 'pmid'.
    :return: Weight adjusted by the minimum age of the connected nodes.
    """

    source_age = next((vs['age'] for vs in graph.vs if vs[key] == edge[0]), default_age)
    target_age = next((vs['age'] for vs in graph.vs if vs[key] == edge[1]), default_age)
    min_age = max(1, min([source_age, target_age]))
    return weight / min_age

def citation_adjusted_weight(edge: tuple, weight, graph: igraph.Graph, default_nr_citations = 100, key: str = 'pmid') -> float:
    """
    Adjusts the weight of an edge based on the number of citations of its connected nodes.

    :param edge: Tuple representing the edge (source, target).
    :param weight: Float value of the initial weight of the edge.
    :param graph: An igraph.Graph object representing the graph.
    :param default_nr_citations: Integer value representing the default number of citations to use if node citation count is not found. Default is 100.
    :param key: String specifying the attribute key to look up node citation count in the graph. Default is 'pmid'.
    :return: Weight adjusted by the minimum citation count of the connected nodes.
    """

    source_citations = next((vs['nr_citations'] for vs in graph.vs if vs[key] == edge[0]), default_nr_citations)
    target_citations = next((vs['nr_citations'] for vs in graph.vs if vs[key] == edge[1]), default_nr_citations)

    min_citations = max(1, min([source_citations, target_citations]))

    return weight / min_citations 

def median_citations(graph: igraph.Graph, workflow:Union[dict,list], default_nr_citations: int = 0) -> int:
    """
    Simply returns the median number citations of all of the primary publications of tools in the workflow.
    
    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param default_nr_citations: An int representing the value one would like to use for tools that dont have a recorded citation number. 

    :return: Integer value of the median number of citations.
    
    """
    if isinstance(workflow, dict):
        pmids = list(workflow['steps'].values())
    elif isinstance(workflow, list):
        pmids = list(set(element for tup in workflow for element in tup))
    else:
        raise TypeError

    total_citations = []

    if len(pmids)==0:
        return 0
    
    for pmid in pmids:
        citation_number = next((vs['nr_citations'] for vs in graph.vs if vs['pmid'] == pmid), default_nr_citations)
        if citation_number:
            total_citations.append(citation_number)

    if total_citations:
        return statistics.median(total_citations)
    else: 
        return None
