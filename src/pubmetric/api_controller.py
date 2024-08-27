from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Optional, List
import numpy as np
import tempfile
import os 
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore

import pubmetric.metrics as met
from pubmetric.workflow import parse_cwl_workflows
from pubmetric.network import create_citation_network

app = FastAPI()

jobstores = {
    'default': MemoryJobStore()
}

scheduler = AsyncIOScheduler(jobstores=jobstores, timezone='Europe/Berlin')

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
    tool_list: Optional[list]

@scheduler.scheduled_job('interval', days=30)
async def periodic_graph_generation():
    """Periodically generates a new citation network graph every 30 days and updates the global path if the graph is successfully created. 
        If the graph file is not found, it logs an error message.

    :return: Dict
        A dictionary containing a message with the new graph path if successful or an error message if the graph file is not found.

    """
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
    """
    Processes an uploaded CWL file to score workflows based on the current citation network graph. Returns scores for the tool- and workflow-level metrics, and ages.

    :param cwl_file: UploadFile
        The uploaded CWL file to be processed.

    :return: ScoreResponse
        A response model containing the computed scores for the workflow; metric and age benchmarks accoring to the Workflomics JSON Schema for Benchmarks.
    """

    graph = await create_citation_network(inpath=latest_output_path, load_graph=True) # should I maybe change the name so it does not contain the date, so you have to look in the file instead, or perhaps it is regenerated outside of the package entrirely
    # Saving the uploaded files temporarily, should this have some type of check so no bad things can be sent? 
    with tempfile.TemporaryDirectory() as temp_dir:

        cwl_file_path = os.path.join(temp_dir, cwl_file.filename)
        with open(cwl_file_path, "wb") as f: # Slightly dumb to open and save and then just open again within the parse workflows function. Shoudl I update parse wf to work with open files?
            f.write(cwl_file.file.read())

        
        workflow = parse_cwl_workflows(cwl_filename=cwl_file_path, graph=graph)  
        pmid_workflow = workflow['pmid_edges'] # for the metrics that do not need to take into account the structure

        # Metrics
        workflow_level_scores =  met.workflow_average_sum(graph, pmid_workflow)
        workflow_desirability = met.calculate_desirability(workflow_level_scores, 10, 400)
        tool_level_scores = met.tool_average_sum(graph, workflow)


        tool_level_output = []
        for tool_name, score in tool_level_scores.items():
            desirability = met.calculate_desirability(score, 10, 400) # TODO make dependent on the highest nr in that particular graph 
            if not score or score == 0:
                score = 'Unknown'
            tool_level_output.append({
                    "desirability": desirability,# based on the 95th percentile of the nr of cocitations in the proteomics graph
                    "label": str(score), # should this be the tool name? or is this what is used on hover? 
                    "value": str(score)
                })

        ages_output = []
        ages = []
        for _, pmid in workflow['steps'].items():
            age = next(tool['age'] for tool in graph.vs if tool['pmid'] == pmid)
            if not age or age == 40:
                age = "Unknown"
                desirability = 0
            else:
                desirability = met.calculate_desirability(age, 3, 20, inverse=True)
            ages.append(age)
            ages_output.append({
                    "desirability": desirability, # Because green == new?  
                    "label": str(age),
                    "value": str(age)
                })
            
        

        metric_benchmark = {
            "unit": "metric",
            "description": "The tool- and workflow-level metric",
            "title": "Pubmetric",
            "steps": tool_level_output,
            "aggregate_value": {
                "desirability": workflow_desirability, # again based on the 95th percentile 
                "value": str(workflow_level_scores)
            }
        }
        age_benchmark = {
            "unit": "age",
            "description": "Ages of primary publications",
            "title": "Age",
            "steps": ages_output,
            "aggregate_value": {
                "desirability": 1.0, # unclear what to put here
                "value": str(np.median(ages)) # median age as the aggregate value? 
            }
        }

    benchmarks = [metric_benchmark, age_benchmark]

    return ScoreResponse(workflow_scores=benchmarks)

@app.post("/recreate_graph/")
async def recreate_graph(graph_request: GraphRequest): # if you want to recreate it with a request
    """
    Recreates the citation network graph based on the provided topic ID and test size. 
    Updates the global graph path if the graph is successfully generated.

    :param graph_request: GraphRequest
        The request model containing the topic ID and test size for graph recreation.

    :return: Dict
        A dictionary containing a message with the new graph path if successful or an error message if the graph file is not found.


    """
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
    
    

