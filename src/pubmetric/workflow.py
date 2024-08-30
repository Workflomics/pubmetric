"""Workflow parsing module"""
import igraph

from cwl_utils.parser import load_document_by_uri

def parse_cwl(graph: igraph.Graph, cwl_filename: str) -> list:
    """
    Function that turns a CWL representation of a workflow into a list of node tuples 
        (edges), where source and target is represented by the pmid of their repecitve 
        primary publication. 

    :param graph: igraph.Graph object representing a co-citation graph.
    :param cwl_filename: String representing the path to the CWL file

    :return: List of tuples representing the edges in the workflow.

    """
    cwl_obj = load_document_by_uri(cwl_filename)

    edges = []
    workflow_steps = {}
    # Extracting edges from the CWL
    for step in cwl_obj.steps:
        step_id = step.id.split("#")[-1]

        # Collecting all step names, and their corresponding pmids
        tool_name = step_id.split('_')[0]
        workflow_steps[step_id] = next((tool['pmid']
                                        for tool in graph.vs
                                        if tool['name'] == tool_name),
                                        None)
        for input_param in step.in_:
            if input_param.source:
                source_step_id = input_param.source.split("#")[-1].split('/')[0]

                if "input_" not in source_step_id: # skips the edges between input and tools

                    edges.append((source_step_id, step_id))

    # Saving the edges in pmid format.
    # OBS that this does not maintain the structure of the workflow if a
        # tool is used more than once since both inctances link to the same pmid
    pmid_edges = []
    for edge in edges:
        source_pmid = next((tool['pmid']
                            for tool in graph.vs
                            if tool['name'] == edge[0].split('_')[0]),
                            None)
        target_pmid = next((tool['pmid']
                            for tool in graph.vs
                            if tool['name'] == edge[1].split('_')[0]),
                            None)
        pmid_edges.append((str(source_pmid), str(target_pmid)))

    workflow = {"edges": edges,
                "steps": workflow_steps, # steps and correspoding pmids
                "pmid_edges": pmid_edges
    }
    return workflow
