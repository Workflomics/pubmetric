import os 
import igraph 
from wfqc.workflow import *



def test_generate_random_workflow():
    """"
    Comparing two igraph graphs "topologically" to assert that the random workflow generated 
    is of the same strucutre as the workflow it was based on, that is, that they are isomorphs. 

    """
    #tool list contains the PmIDs currently in the tool_metadata testfile (10/07/2025), a subset of the bio.tools proteomics domain
    tool_list = ['38745111', '38110863', '23051804', '23051804', '23148064', '38681522', '38703894', '38658834', '38498849', '38233783', '38552327', '38517698', '38566187', '37328457', '38567734', '38711578', '38711760', '24909410', '25631240', '14632076', '12403597', '14976030', '29400476']
    workflow = [('14976030','14632076' )  , ('14976030','12403597')  , ('14632076','29400476')  , ('12403597', '29400476')]
    radnom_workflow = generate_random_workflow(tool_list=tool_list, workflow=workflow) # TDO: needs to be updated to support the new structure 

    graph = igraph.Graph.TupleList(workflow)
    random_graph = igraph.Graph.TupleList(radnom_workflow)

    assert graph.isomorphic(random_graph) # TODO: use this to test network funcitons

def test_generate_pmid_edges(shared_datadir):
    metadata_filename = os.path.join(shared_datadir, "tool_metadata_test20_topic_0121_20250705.json")

    name_workflow = [ ('XTandem', 'ProteinProphet'), ('XTandem', 'PeptideProphet'), ('ProteinProphet', 'StPeter'), ('PeptideProphet', 'StPeter') ]
    expected_tuple_workflow = [('14976030','14632076' )  , ('14976030','12403597')  , ('14632076','29400476')  , ('12403597', '29400476')  ]
                            # [ (XTandem, ProteinProphet), (XTandem, PeptideProphet), (ProteinProphet, StPeter), (PeptideProphet, StPeter) ]

    faulty_name_workflow = [ ('XTandem', 'ProteinProphet'), ('XTandem', 'NotATOOL'), ('ProteinProphet', 'StPeter'), ('NotATOOL', 'StPeter') ]

    reconnected_workflow = generate_pmid_edges(metadata_filename, name_workflow)
    reconnected_faulty_workflow = generate_pmid_edges(metadata_filename, faulty_name_workflow, handle_missing='reconnect')
    removed_faulty_workflow = generate_pmid_edges(metadata_filename, faulty_name_workflow, handle_missing='remove')
    kept_faulty_workflow = generate_pmid_edges(metadata_filename, faulty_name_workflow, handle_missing='keep')

    assert sorted(reconnected_workflow) == sorted(expected_tuple_workflow) # A wofklow where all PmIDs are in the metadatafile should not be changed
    assert len(reconnected_faulty_workflow) == 3 # the two edges containing 'NotATOOL' should be turned into a single edge ('XTandem', 'StPeter')
    assert len(removed_faulty_workflow) == 2 # the two edges containing 'NotATOOL' are removed
    assert len(kept_faulty_workflow) == 4 and 'None' in kept_faulty_workflow[1] # the two edges containing 'NotATOOL' will contain a None 
                                                #TODO this should not be a string none but a none none


def test_parse_cwl_workflow_update(shared_datadir):
    cwl_filename = os.path.join(shared_datadir, "candidate_workflow_repeated_tool.cwl")
    metadata_filename = os.path.join(shared_datadir, "tool_metadata_test20_topic_0121_20250705.json")

    workflow = parse_cwl_workflows(cwl_filename,metadata_filename )  
    
    assert workflow['edges'] == [('XTandem_01', 'ProteinProphet_02'), ('ProteinProphet_02', 'StPeter_04'), ('XTandem_03', 'StPeter_04')]
