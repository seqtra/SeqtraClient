import os
import datetime
import requests
from typing import Optional, Dict, Any
import json
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import uuid


def send_request(url, req_body=None, headers=None, files=None, data=None):
    start = datetime.datetime.now()
    response = requests.post(
        url,
        json=req_body,
        files=files,
        headers=headers,
        data=data
    )
    end = datetime.datetime.now()
    return response, end - start

def upload_multiple_files(
        file_paths: list[str],
        url: str = '/upload',
        headers: Optional[Dict[str, str]] = None,
        extra_data: Optional[Dict[str, Any]] = None
):
        
        # Prepare headers
        headers = headers or {}
            
        # Prepare the files
        files = []
        opened_files = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file = open(file_path, 'rb')
            opened_files.append(file)
            files.append(
                ("files", (os.path.basename(file_path), file, 'application/octet-stream'))
            )
        # Send the request
        extra_data_json = {"req_params": json.dumps(extra_data)} if extra_data else {}
        response, time = send_request(
            url,
            headers=headers,
            files=files,
            data=extra_data_json
        )
            
        # Ensure all files are closed
        for file in opened_files:
            file.close()
                
        return response, time
    
    
def check_response(resp):
    try:
        resp.raise_for_status()
    except Exception as e:
        resp = e.response.json()
        message = resp["detail"] if resp.get("detail") else resp["message"]
        raise Exception(message)
    
def delete_request(url, project_name, headers):
    complete_url = os.path.join(url, "delete", project_name)
    
    response = requests.delete(complete_url, headers=headers)
    
    return response

def visualize_graph(graph, chunks):
    id2chunk = {v: k for k,v in chunks.items()}
    p_graph = {
        "nodes": [{"data": {"chunk_id": id2chunk[n["id"]] , **{k:v for k, v in n.items()}} if n["label"] == "chunk" else n} for n in graph["nodes"]],
        "edges": [{"data": {"id": uuid.uuid4().hex, "source": n["source_id"], "target": n["target_id"], "label": n["label"]}} for n in graph["edges"]]
    }
    node_styles = [
        NodeStyle("chunk", "#FF7F3E",caption="chunk_id", icon="description"),
        NodeStyle("topic", "#2A629A", caption="text", icon="inventory"),
    ]

    edge_styles = [
        EdgeStyle("common_topic_of", color="#2A629A", caption='label', directed=True, curve_style="haystack"),
        EdgeStyle("has_link", color="#FF7F3E", caption='label', directed=True, curve_style="haystack"),
    ]
    st_link_analysis(p_graph,"cola", node_styles, edge_styles)