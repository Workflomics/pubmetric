from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Dict
import tempfile
import os 
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore

from pubmetric.metrics import *
from pubmetric.workflow import parse_cwl_workflows
from pubmetric.network import create_citation_network

app = FastAPI()

jobstores = {
    'default': MemoryJobStore()
}

scheduler = AsyncIOScheduler(jobstores=jobstores, timezone='Asia/Kolkata')

latest_output_path = "out_20240801231111"


@asynccontextmanager
async def lifespan(application: FastAPI):
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

class ScoreResponse(BaseModel):
    workflow_scores: List

class GraphRequest(BaseModel):
    topic_id: str
    test_size: str

@scheduler.scheduled_job('interval', days=30)
async def periodic_graph_generation():
    global latest_output_path
    try:
        new_output_path = await create_citation_network(topic_id="default", test_size=20, return_path = True)
        if os.path.exists(new_output_path + "/graph.pkl"):
            latest_output_path = new_output_path
            return {"message": f"Graph and metadata file recreated successfully New graph path: {latest_output_path}."}
        else:
            return {"error": "Error: Generated graph file not found."}
    except Exception as e:
        return {"error": f"An error occurred while recreating the graph: {e}. The previous graph will continue to be used."}
scheduler.add_job(periodic_graph_generation, 'interval', days=30)

@app.post("/score_workflows/", response_model=ScoreResponse)
async def score_workflows(cwl_file: UploadFile = File(None)):

    graph = await create_citation_network(inpath=latest_output_path, load_graph=True) # should I maybe change the name so it does not contain the date, so you have to look in the file instead, or perhaps it is regenerated outside of the package entrirely
    # Saving the uploaded files temporarily, should this have some type of check so no bad things can be sent? 
    with tempfile.TemporaryDirectory() as temp_dir:

        cwl_file_path = os.path.join(temp_dir, cwl_file.filename)
        with open(cwl_file_path, "wb") as f: # Slightly dumb to open and save and then just open again within the parse workflows function. Shoudl I update parse wf to work with open files?
            f.write(cwl_file.file.read())

        
        workflow = parse_cwl_workflows(cwl_filename=cwl_file_path, graph=graph)  
        pmid_workflow = workflow['pmid_edges'] # for the metrics that do not need to take into account the structure

        # Metrics
        workflow_level_scores =  workflow_average_sum(graph, pmid_workflow)
        tool_level_scores = tool_average_sum(graph, workflow)

        tool_level_output = []
        for tool_name, score in tool_level_scores.items():
            tool_level_output.append({
                    "desirability": 8.0,# based on the 95th percentile of the nr of cocitations in the proteomics graph
                    "label": score, # should this be the tool name? or is this what is used on hover? 
                    "value": score
                })

        ages_output = []
        ages = []
        for _, pmid in workflow['steps'].items():
            age = next(tool['age'] for tool in graph.vs if tool['pmid'] == pmid)
            ages.append(age)
            ages_output.append({
                    "desirability": 0, # Because green == new?  
                    "label": age, # should this be the tool name? or is this what is used on hover? 
                    "value": age
                })


        
        metric_benchmark = {
            "unit": "metric",
            "description": "The tool- and workflow-level metric",
            "title": "Pubmetric",
            "steps": tool_level_output,
            "aggregate_value": {
                "desirability": 8.0, # again based on the 95th percentile 
                "value": workflow_level_scores 
            }
        }
        age_benchmark = {
            "unit": "age",
            "description": "Ages of primary publications",
            "title": "Age",
            "steps": ages_output,
            "aggregate_value": {
                "desirability": 1, # unclear what to put here
                "value": np.median(ages) # median age as the aggregate value? 
            }
        }

    benchmarks = [metric_benchmark, age_benchmark]   

    return ScoreResponse(workflow_scores=benchmarks)

@app.post("/recreate_graph/")
async def recreate_graph(graph_request: GraphRequest): # if you want to recreate it with a request
    global latest_output_path
    try:
        new_output_path = await create_citation_network(topic_id=graph_request.topic_id, test_size=20, return_path=True)
        if os.path.exists(os.path.join(new_output_path, "graph.pkl")):
            latest_output_path = new_output_path
            return {"message": f"Graph and metadata file recreated successfully New graph path: {latest_output_path}."}
        else:
            return {"error": "Error: Generated graph file not found."}
    except Exception as e:
        return {"error": f"An error occurred while recreating the graph: {e}. The previous graph will continue to be used."}
    
    

