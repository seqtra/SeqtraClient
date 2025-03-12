import os
import datetime
import requests
from typing import Optional, Dict, Any
import json


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