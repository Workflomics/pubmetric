import os
import tempfile
from typing import List, Optional
from contextlib import asynccontextmanager

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import numpy as np

import pubmetric.metrics
import pubmetric.network
import pubmetric.workflow


app = FastAPI()

jobstores = {
    'default': MemoryJobStore()
}

scheduler = AsyncIOScheduler(jobstores=jobstores, timezone='Europe/Berlin')



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
    topic_id: Optional[str] = None
    test_size: Optional[int] = None
    tool_selection: Optional[List[str]] = None
    inpath: Optional[str] = ''



@scheduler.scheduled_job('interval', days=30)
async def periodic_graph_generation():
    """Periodically generates a new citation network graph every 30 days and updates
        the global path if the graph is successfully created. 
        If the graph file is not found, it logs an error message.

    :return: Dict
        A dictionary containing a message with the new graph path if successful 
        or an error message if the graph file is not found.

    """
    temporary_path = "new_cocitation_graph/"
    try:
        await pubmetric.network.create_network(topic_id = None,
                                               test_size = 20, # TODO rm
                                               outpath = temporary_path)

        check_graph_creation(temporary_path=temporary_path)

        return {"message":
            f"Graph and metadata file recreated successfully!"}
    except Exception as e:
        return {"error": f"An error occurred while recreating the graph: {e}."
                "The previous graph will continue to be used."}
scheduler.add_job(periodic_graph_generation, 'interval', days=30)


@app.post("/score_workflow/", response_model=ScoreResponse)
async def score_workflow(cwl_file: UploadFile = File(None)):
    """
    Processes an uploaded CWL file to score workflows based on the current citation
    network graph. Returns scores for the tool- and workflow-level metrics, and ages.
    :param cwl_file: UploadFile
        The uploaded CWL file to be processed.

    :return: ScoreResponse
        A response model containing the computed scores for the workflow;
        metric and age benchmarks accoring to the Workflomics JSON Schema for Benchmarks.
        See https://workflomics.readthedocs.io/en/latest/dev/standards.html for a detailed
        description. 
    """

    graph = await pubmetric.network.create_network(inpath="data/out", load_graph=True) 
    # data/out used as the latest created graph
    # TODO: should be configurable
    with tempfile.TemporaryDirectory() as temp_dir:

        cwl_file_path = os.path.join(temp_dir, cwl_file.filename)
        with open(cwl_file_path, "wb") as f: # Slightly dumb to open and save and then just 
                                                # open again within the parse workflows function. 
                                                # Shoudl I update parse wf to work with open files?
            f.write(cwl_file.file.read())

        
        workflow = pubmetric.workflow.parse_cwl(cwl_filename=cwl_file_path,
                                                graph=graph)
        pmid_workflow = workflow['pmid_edges']

        # Metrics
        workflow_level_score =  pubmetric.metrics.workflow_average(graph=graph,
                                                                workflow=pmid_workflow)
        workflow_desirability = pubmetric.metrics.calculate_desirability(score=workflow_level_score,
                                                                         thresholds= [0, 400])
        tool_level_scores = pubmetric.metrics.tool_average_sum(graph, workflow)


        tool_level_output = []
        for tool_name, score in tool_level_scores.items():
            # lower since they are multiplied by the desirability of workflows
            desirability = pubmetric.metrics.calculate_desirability(score=score,
                                                                    thresholds= [0,200])

            if not score or score == 0:
                score = 'Unknown'
            tool_level_output.append({
                    "desirability": desirability,
                    "label": f'{tool_name.split("_")[0]}: {score}',
                    "value": str(score)
                })

        ages_output = []
        ages = []
        for tool_name, pmid in workflow['steps'].items():
            age = next((tool['age'] for tool in graph.vs if tool['pmid'] == pmid), None)
            if not age or age > 40: # igraph requires all values of same type, hence >40 is None
                age = "Unknown"
                desirability = 0
            else:
                # capped by putting the upper threshold above maximum 
                desirability = pubmetric.metrics.calculate_desirability(score=age,
                                                                        thresholds= [0, 45],
                                                                        inverted=True,
                                                                        transform = False) 
            ages.append(age)
            ages_output.append({
                    "desirability": desirability, # Because green == new?  
                    "label":  f'{tool_name.split("_")[0]}: {age}',
                    "value": str(age)
                })
            
        
        metric_benchmark = {
            "unit": "metric",
            "description": "The tool- and workflow-level metric",
            "title": "Pubmetric",
            "steps": tool_level_output,
            "aggregate_value": {
                "desirability": workflow_desirability, 
                "value": str(workflow_level_score)
            }
        }
        age_benchmark = {
            "unit": "age",
            "description": "Time since release of primary publications",
            "title": "Age",
            "steps": ages_output,
            "aggregate_value": {
                "desirability": 1.0, # unclear what to put here
                "value": str(np.median([int(age['value']) for age in ages_output if age["value"] != "Unknown"]))
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
        A dictionary containing a message with the new graph path if successful or an error
        message if the graph file is not found.


    """
    temporary_path = "new_cocitation_graph/"
    try:
        await pubmetric.network.create_network(topic_id = graph_request.topic_id,
                                               tool_selection = graph_request.tool_selection,
                                               test_size = graph_request.test_size,
                                               inpath = graph_request.inpath,
                                               outpath = temporary_path)
        check_graph_creation(temporary_path=temporary_path)
        return {"message":
            f"Graph and metadata file recreated successfully!"}
    except Exception as e:
        return {"error": f"An error occurred while recreating the graph: {e}."
                "The previous graph will continue to be used."}
    


def check_graph_creation(temporary_path: str):
    """
    Checks that the new files have been created. If successful, removes the old ones and updates the
    new ones to have the 'base' name.

    :param temporary_path: The directory currently storing the newly generated graph
    
    :raises FileNotFoundError: If the new graph files were not created correctly. This error is raised
        when the expected files (`graph.pkl` and `tool_metadata.json`) are not found in the
        `temporary_path` directory.
    """
    graph_file_path = os.path.join(temporary_path, "graph.pkl")
    metadata_file_path = os.path.join(temporary_path, "tool_metadata.json")
    if os.path.exists(graph_file_path) and os.path.exists(metadata_file_path):
        base_path = "cocitation_graph/"
        if os.path.exists(base_path):
            # Remove old files and the old directory, to rename the new one to the old
            # TODO: should only be removed when th temp one is already renamed?
            for file in os.listdir(base_path):
                os.remove(os.path.join(base_path, file))
            os.rmdir(base_path)
        os.rename(temporary_path, base_path)
        return
    else: # remove the temporary folder if graph creation did not work
        if os.path.exists(temporary_path):
            for file in os.listdir(temporary_path):
                os.remove(os.path.join(temporary_path, file))
            os.rmdir(temporary_path)
        raise FileNotFoundError("New graph files were not created correctly.")
