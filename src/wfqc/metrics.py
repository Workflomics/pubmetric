import igraph
import numpy as np
import math
import statistics
from typing import List

#TODO: all metrics that need to think about  workflow structure need to be updated to work with the new workflow representation 
# for ex: compelte tree needs to take into account the repeated tool several times


# General functions for interation with graph 

def get_node_ids(graph: igraph.Graph, key:str= "name") -> dict:
    """"
    Maps node names to their igraph IDs.

    :param graph: igraph.Graph 
    :param key: String indicating which of ID and name shoudl be used as key in the mapping dictionary

    :return: Dictionary mapping names to igraph IDs

    :raises ValueError: if the key is not either name or index TODO: should I have this restiction? could have other mappings 
    """
    if key == 'name':
        return {v['name']:v.index for v in graph.vs}
    elif key == 'index':
        return {v.index:v['name'] for v in graph.vs}
    else:
        raise ValueError("Not a valid key")


def get_graph_edge_weight(graph: igraph.Graph, edge: tuple) -> float:
    """
    Retrieves the weight of an edge between a pair of nodes. 

    :param graph: igraph.Graph object with weighted edges
    :param edge: A tuple of node names

    :return: A float representing the weight of a graph
    """

    id_dict = get_node_ids(graph) # TODO: cnat regen this every time. Move out? 

    if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
        return None # if either node is not in the graph, then the weight is None
    try:
        source = edge[0]
        target = edge[1]
        weight = graph.es.find(_between=((id_dict[source],), (id_dict[target],)))['weight']
    except:
        weight = 0.0 # if node are in the graph but they are not connected, then the weight of an edge between them is None

    return float(weight)




# Tool level metric

def tool_average_sum(graph: igraph.Graph, workflow: list) -> float:
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

    step_scores ={}
    for step in steps: 
        score = []
        for edge in edges:
            if step in edge:
                pmid_source = next(pmid for step_id, pmid in workflow['steps'].items() if step_id == edge[0] )
                pmid_target = next(pmid for step_id, pmid in workflow['steps'].items() if step_id == edge[1] )

                score.append( get_graph_edge_weight(graph, edge = (pmid_source, pmid_target) ) )
        if score:
            step_scores[step] = sum(score)/len(score) 
        else:
            step_scores[step] = 0

    return step_scores


# Workflow level metric
def workflow_average_sum(graph: igraph.Graph, workflow: list) -> float:
    """
    Calculates the sum (or average if normalised) of edge weights within a workflow.

    :param graph: An igraph.Graph co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    

    :return: Float value of the average sum metric calculated on the edges of the workflow.
    """

    if not workflow: # if there are no edges
        return 0 

    aggregated_weight = 0
    for edge in workflow:
        weight = get_graph_edge_weight(graph, edge) or 0
        aggregated_weight += weight

    return round(float(aggregated_weight/len(workflow) ), 3)



def connectivity(graph: igraph.Graph, workflow: list) -> float:
    """
    Calculates the sum of the edge weights between all possible pairs of tools in a workflow.
    Named after the degree of connectivity - how close it is to being a complete graph - though this is weighted.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: Dictionary representing the workflow. TODO reference schema
    

    :return: Float value of the logarithmic product metric.
    """   

    step_dict = list(workflow['steps'].items())
    print(step_dict)
    nr_steps = len(step_dict)

    if nr_steps == 0:
        return 0.0

    total_weight = 0
    for i in range( nr_steps ):
        for j in range(i + 1, nr_steps ):
            weight = get_graph_edge_weight(graph, (step_dict[i][1], step_dict[j][1])) or 0
            total_weight += weight # why dont I use this everywhere, skips the if else? TODO!

    nr_possible_edges = nr_steps * (nr_steps - 1) // 2

    return total_weight/nr_possible_edges

def workflow_weighted_connectivity(graph: igraph.Graph, workflow: dict, factor:float = 1.0):
    """
    Combination metric of the sum_metric() and complete_tree() metrics, where the edges in the workflow are given more (or less, but I would not recommend that) importance.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: Dictionary representing the workflow. TODO schema
    :param factor: Float value specifying how much extra weight the edges that are in the workflow are given relative to the rest of the edges between nodes.
        A factor of 0 gives no extra weight to the workflow edges and thus will give the same value as the regular complete_tree() metric. 

    :return: Float value of the complete three and sum combination metric.
    """   
    pmid_workflow = workflow['pmid_edges'] 
    workflow_edge_score = workflow_average_sum(graph, pmid_workflow)
    all_possible_edges_score = connectivity(graph, workflow)

    none_workflow_edges_score = all_possible_edges_score - workflow_edge_score

    workflow_weighted_score = none_workflow_edges_score + workflow_edge_score * factor
    return float( workflow_weighted_score )

def transformed_workflow_average_sum(graph: igraph.Graph, workflow: List[tuple], transform: str = "log") -> float:
    """
    Calculates the average sum of the logarithm of edge weights.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.

    :return: Float value of the log sum metric.
    """
    if not workflow: # If workflow is an empty list
        return 0 

    aggregated_weight = 0
    for edge in workflow:
        weight = get_graph_edge_weight(graph, edge) or 0
        if transform == "log":
            aggregated_weight += math.log(weight + 1)  # Log of weight + 1 to avoid -inf
        elif transform == "sqrt":
            aggregated_weight += math.sqrt(weight)
        else:
            raise ValueError(f"Unsupported transformation: {transform}")

    return round(float(aggregated_weight/len(workflow) ), 3)


def degree_workflow_average_sum(graph: igraph.Graph, workflow: list) -> float:
    """
    'Normalises' edge weights by the average degree of the nodes and sums them up.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    

    :return: Float value of the degree-normalised sum metric.
    """

    if not workflow: # If workflow is an empty list
        return 0 
    
    aggregated_weight = 0
    id_dict = get_node_ids(graph)
    for edge in workflow:
        if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']: # igraph attribute "name" stores the pmids
            continue

        edge_weight = get_graph_edge_weight(graph, edge)
        if edge_weight is None: # skip the rest of the calculations
            continue

        source_degree = graph.vs[id_dict[edge[0]]].degree()
        target_degree = graph.vs[id_dict[edge[1]]].degree()

        avg_degree = np.mean([source_degree, target_degree])

        normalised_edge_weight = edge_weight / avg_degree

        aggregated_weight += normalised_edge_weight

    return round(float(aggregated_weight/len(workflow) ), 3)

def workflow_edge_product(graph: igraph.Graph, workflow: list) -> float:
    """
    Calculates the product of edge weights in a workflow

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    

    :return: Float value of the product metric .
    """    
    if not workflow: # If workflow is an empty list
        return 0 
    
    weights = []
    
    for edge in workflow:
        weight = get_graph_edge_weight(graph, edge) or 0
        weights.append(weight)

    nonzero_weights = [w for w in weights if w!=0]  #only use nonzero weights
    if nonzero_weights:
        score =  np.prod(nonzero_weights) / len(workflow) 
        return round(float(score), 3)
    else:
        return 0.0  # If there are no weights
    

def log_workflow_edge_product(graph: igraph.Graph, workflow: list) -> float:
    """ 
    Calculates the product of the logarithm of the edge weights in a workflow

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    

    :return: Float value of the logarithmic product metric.
    """
    if not workflow: # If workflow is an empty list
        return 0 
    
    weights = []
    for edge in workflow:
        weight = get_graph_edge_weight(graph, edge) or 0

        weights.append( math.log( weight + 1)) # adding 1 to avoid - inf

    nonzero_weights = [w for w in weights if w!=0]  #only use nonzero weights
    if nonzero_weights:
        score =  np.prod(nonzero_weights) / len(workflow) 
        return round(float(score), 3)
    else:
        return 0.0  # If there are no weights


def age_norm_sum_metric(graph, workflow, metadata_file) -> float:
    """
    Normalises edge weights by the average ages of the nodes and sums them up.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param metadata_file: The dictionary of tool matadata. TODO: QUESTION: some specific way of referencing a file with a certain type/format of contents?
    

    :return: Float value of the age-normalised sum metric.

    """
    return # needs to be updated to fit new format - age shoudl be part of metadatafile creation TODO
    
def connectivity_age_norm(graph, workflow, metadata_file):
    """
    Combination metric of the age_norm_sum_metric() and complete_tree() metrics, where the edges in the workflow are given more importance.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param metadata_file: The dictionary of tool matadata. TODO: QUESTION: some specific way of referencing a file with a certain type/format of contents?
    

    :return: Float value of the age-normalised complete_tree() metric.

    """
    return # needs to be updated to fit new format - age shoudl be part of metadatafile creation TODO

def connectivity_min(graph, workflow): 
    """
    The complete_tree() metric which punishes single bad links. 

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    

    :return: Float value of the bad edge penalising complete_tree() metric.

    """
    return #sum(total_weight)*min(total_weight)/n  # needs to be updated to fit new format - age shoudl be part of metadatafile creation TODO


def complete_citation(graph, workflow, citation_data_file):
    """
    A variation of the complete_tree() metric, where the edges are divided by the mean number of citations of the source and target.

    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param metadata_file:  A string of the name of the JSON file containing tool meta data. TODO: QUESTION: some specific way of referencing a file with a certain type/format of contents?
    

    :return: Float value of the citation-normalised complete_tree() metric.

    """

        # citations_source = [tool['nrCitations'] for tool in citation_data_file['tools'] if tool['pmid'] == tool_list[i]]
        # citations_target = [tool['nrCitations'] for tool in citation_data_file['tools'] if tool['pmid'] == tool_list[j]]
        # citations = [c for c in (citations_source + citations_target) if c]

        # if citations:
        #     total_weight.append(weight/citations)
        # else:
        #      total_weight.append(weight)
    return #sum(total_weight)*min(total_weight)/n  # needs to be updated to fit new format - age shoudl be part of metadatafile creation TODO

def citations(workflow:list, citation_data_file:str) -> int:
    """
    Simply returns the median number citations of all of the primary publications of tools in the workflow.
    
    :param graph: An igraph.Graph object representing the co-citation graph.
    :param workflow: List of edges (tuples of tool PmIDs) representing the workflow.
    :param citation_data_file: A string of the name of the JSON file containing citation data. TODO: QUESTION: some specific way of referencing a file with a certain type/format of contents?

    :return: Integer value of the median number of citations.
    
    """
    #TODO needs update
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)  
    

    total_citations = []
    tool_list = list(tools)
    n = len(tool_list)
    
    if n==0:
        return 0
    
    for tool in tool_list:
        citation_number = [t['nrCitations'] for t in citation_data_file['tools'] if t['pmid'] == tool]
        if citation_number:
            total_citations.append(citation_number[0]) #TODO: this does not work if no results

    if total_citations:
        return statistics.median(total_citations)
    


### BELOW needs updates, not because it does not work, but because it is dumb


# TODO this shoudl just be an option in the previous metric, only diff is if multiplied or divided
def mult_age_norm_sum_metric(graph, workflow, metadata_file):
    weights = []

    id_dict = get_node_ids(graph)

    for edge in workflow:

        if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
            weights.append(0)
            continue

        edge_weight = get_graph_edge_weight(graph, edge)

        source_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[0]]
        target_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[1]]

        ages = [age for age in (source_age + target_age) if age ]
        
        
        avg_age = np.mean( ages ) # perhaps too harsh 

        normalised_edge_weight = edge_weight* avg_age

        weights.append(normalised_edge_weight)

    calculated_weights = [w for w in weights if w] 
    if calculated_weights:

        norm_score = sum(calculated_weights)/len(weights) # avg cocitations
        return float(norm_score)

    
def mult_complete_tree_age_norm(graph, workflow, metadata_file): # TODO this shoudl just be an option in the previous metric, only diff is if multiplied or divided
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)
    
    total_weight = 0
    tool_list = list(tools)
    n = len(tool_list)
    
    if n == 0:
        return 0

    for i in range(n):
        for j in range(i + 1, n):
            edge = (tool_list[i], tool_list[j])
            
            if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
                continue

            edge_weight = get_graph_edge_weight(graph, edge)
            if not edge_weight:
                continue

            source_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[0]]
            target_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[1]]
            ages = [age for age in (source_age + target_age) if age]

            if ages:
                avg_age = np.mean(ages)
                normalised_edge_weight = edge_weight * avg_age
                total_weight += normalised_edge_weight


    return float(total_weight) / n


def sub_complete_tree_age_norm(graph, workflow, metadata_file): #TODO: make this an option in above metric
    tools = set()
    for edge in workflow:
        if edge:
            tools.update(edge)
    
    total_weight = 0
    tool_list = list(tools)
    n = len(tool_list)
    
    if n == 0:
        return 0

    for i in range(n):
        for j in range(i + 1, n):
            edge = (tool_list[i], tool_list[j])
            
            if edge[0] not in graph.vs['name'] or edge[1] not in graph.vs['name']:
                continue

            edge_weight = get_graph_edge_weight(graph, edge)
            if not edge_weight:
                continue

            source_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[0]]
            target_age = [tool['pubDate'] for tool in metadata_file['tools'] if tool['pmid'] == edge[1]]
            ages = [age for age in (source_age + target_age) if age]

            if ages:
                avg_age = np.mean(ages)
                normalised_edge_weight = edge_weight / (2025 - avg_age) # 2025 so no zero div
                total_weight += normalised_edge_weight
            else:
                continue # nrom bu mean?

    return float(total_weight) / n 


