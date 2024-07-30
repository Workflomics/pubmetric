from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Dict
import tempfile

from wfqc.metrics import *
from wfqc.workflow import parse_cwl_workflows
from wfqc.network import create_citation_network


app = FastAPI()

class ScoreResponse(BaseModel):
    workflow_scores: Dict

class GraphRequest(BaseModel):
    topic_id: str

@app.post("/score_workflows/", response_model=ScoreResponse)
async def score_workflows(file: UploadFile = File(None)):
    workflow_scores = {"score": 1}
    return ScoreResponse(workflow_scores=workflow_scores)

@app.post("/recreate_graph/")
async def recreate_graph(graph_request: GraphRequest):
    
    graph = create_citation_network(loadData=False, testSize=10) 
    some_edges = graph.es['weight'][0:10]
    return {"message": f"Graph and metadata file recreated successfully. Some graph edges: {some_edges}"}
