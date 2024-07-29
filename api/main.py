from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import tempfile

from wfqc.network import create_citation_network
from wfqc.metrics import * # or the metrics Ill actually use

app = FastAPI()

# resåponse model for the requests to validate output type?
class ScoreResponse(BaseModel):
    workflow_scores: Dict # probably a dictionary of some kind, a json file - need to specify levels 

# request model for recreating graph and metadata
class GraphRequest(BaseModel):
    topic_id: str # could also put output path here 

# Should there be a request model also for the files? to check if bad files or sth?
class CwlUploadRequest(BaseModel):
    files: Any # not any- files

# Running metrics on workflows and returning scores - endpoint 1
@app.post("/score_workflows/", response_model=ScoreResponse)   
async def score_workflows(files: List[UploadFile] = File(...)): # Is it actual files being uploaded?
    
    path_to_data = "" # where does one store things?  
    metadata_filename = os.path.join(path_to_data, "metadatafilename.json")  
    
    graph = create_citation_network(inpath=path_to_data) # should I maybe change the name so it does not contain the date, so you have to look in the file instwead
    
    workflow_scores = {}
    # Saving the uploaded files temporarily, should this have some type of check so no bad things can be sent? 
    with tempfile.TemporaryDirectory() as temp_dir: 
        file_paths = []
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f: # Slightly dumb to open and save and then just open again within the parse workflows function. Shoudl I update parse wf to work with open files?
                f.write(file.file.read())
            file_paths.append(file_path)
        
        for file_path in file_paths:
            workflow = parse_workflows(file_path, metadata_filename)
            
            workflow_level_scores = {}
            workflow_level_scores['metric1'] = metric1(workflow, graph, metadata_filename)
            workflow_level_scores['metric2'] = metric2(workflow, graph, metadata_filename)
            # etc 

            tool_level_scores = {}
            tool_level_scores['metric1'] = toolmetric1(workflow, graph, metadata_filename)
            tool_level_scores['metric2'] = toolmetric2(workflow, graph, metadata_filename)
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
