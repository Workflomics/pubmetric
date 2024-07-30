from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import tempfile

from wfqc.network import create_citation_network
from wfqc.metrics import * # or the metrics Ill actually use
from wfqc.workflow import parse_cwl_workflows

app = FastAPI()

# response model for the requests to validate output type?
class ScoreResponse(BaseModel):
    workflow_scores: Dict # probably a dictionary of some kind, a json file - need to specify levels 

# request model for recreating graph and metadata
class GraphRequest(BaseModel):
    topic_id: str # could also put output path here 

# # Should there be a request model also for the files? to check if bad files or sth?
# class CwlUploadRequest(BaseModel):
#     files: Any # not any- files

# Running metrics on workflows and returning scores - endpoint 1
@app.post("/score_workflows/", response_model=ScoreResponse)   
async def score_workflows(file: UploadFile = File(None)): # or None for testing!! # Is it actual files being uploaded?
    
    path_to_data = "../../out_202407041439" # where does one store things later?  
    # metadata_filename = os.path.join(path_to_data, "metadatafilename.json")  
    metadata_filename = "../../../tool_metadata_topic_0121_20240703.json"
    graph = create_citation_network(inpath=path_to_data) # should I maybe change the name so it does not contain the date, so you have to look in the file instead, or perhaps it is regenerated outside of the package entrirely
    
    workflow_scores = {}
    # Saving the uploaded files temporarily, should this have some type of check so no bad things can be sent? 
    with tempfile.TemporaryDirectory() as temp_dir: 

        # file_path = os.path.join(temp_dir, file.filename)
        # with open(file_path, "wb") as f: # Slightly dumb to open and save and then just open again within the parse workflows function. Shoudl I update parse wf to work with open files?
        #     f.write(file.file.read())

        file_path = "../../workflows/workflomics/candidate_workflow_1.cwl"

        workflow = parse_cwl_workflows(file_path, metadata_filename)
        
        workflow_level_scores = {}
        workflow_level_scores['connectivity_average'] = workflow_level_average_sum(graph, workflow)
        pmid_workflow = ['pmid_edges'] # for the metrics that do not need to take into account the structure

        workflow_level_scores['workflow_level_average_sum'] = workflow_level_average_sum(graph, pmid_workflow)
        # etc 

        tool_level_scores = {}
        tool_level_scores['tool_level_average_sum'] = tool_level_average_sum(graph, workflow)
        # etc 

        scores = {'workflow_level_scores': workflow_level_scores,
                    'tool_level_scores': tool_level_scores
                    }
        
        workflow_id = file.filename  # filename as the workflow id
        workflow_scores[workflow_id] = scores # do I want to save any other info?
    
    return ScoreResponse(workflow_scores=workflow_scores)

# Recreateíng graph and metadata file - endpoint 2
@app.post("/recreate_graph/")
async def recreate_graph(graph_request: GraphRequest): # this should be done on a schedule, is that supposed to be within my package or the main one? can I set up somethign taht runs this once a week?
    try:                                                # If I setup sth like that my own messy checking within the create graph function would not be becessary, whic would be nice to get rid of
        graph = create_citation_network(topicID=graph_request.topic_id, Loaddata=False)
        # how make sure this is kept in some data directory?
        # OBS here we put graph in path_to_data
        return {"message": "Graph and metadata file recreated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
