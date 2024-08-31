import os
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from pubmetric.api_controller import app  

client = TestClient(app)

def test_score_workflow(shared_datadir):
    """Testing the /score_workflow/ endpoint."""
    with open(os.path.join(shared_datadir, 'candidate_workflow_repeated_tool.cwl'), "rb") as file:
        response = client.post("/score_workflow/", files={"cwl_file": file})
    assert response.status_code == 200
    assert "workflow_scores" in response.json()

def test_recreate_graph():
    """Testing the /recreate_graph/ endpoint.
    Using mock methods since the generation relies on specific placements and removals of files"""
    data = {
        "topic_id": "topic_121",
        "test_size": None,
        "tool_selection": None,
        "inpath": ""
    }

    # Mocking the filesystem operations and the check_graph_creation function
    with patch("pubmetric.api_controller.os.path.exists") as mock_exists, \
         patch("pubmetric.api_controller.check_graph_creation") as mock_check_graph_creation:

        mock_exists.side_effect = lambda path: path in [
            "new_cocitation_graph/graph.pkl",
            "new_cocitation_graph/tool_metadata.json",
            "cocitation_graph/"
        ]
        mock_check_graph_creation.return_value = None  #do nothing

        response = client.post("/recreate_graph/", json=data)

        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()['message'] == ("Graph and metadata file recreated successfully!")

