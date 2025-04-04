from dataclasses import dataclass
import os
import glob

from src.utils import send_request, upload_multiple_files, check_response, delete_request

@dataclass
class SeqtraClient:
    api_token: str
    project_name: str
    url: str = "http://0.0.0.0:8000/"
    llm: str = "claude"
    llm_key: str = "Your Claude API Key"
    
    def __post_init__(self):
        self.headers = {
            "Seqtra-token": self.api_token
        }
        self.init_req_body = {
            "project_name": self.project_name,
            "llm": self.llm,
            "llm_key": self.llm_key
        }
        init_response, time = send_request(os.path.join(self.url, "init"), req_body=self.init_req_body, headers=self.headers)
        check_response(init_response)
        self.init_status = init_response.json()["message"]
        print(self.init_status)
        print("Initialization time:", time)
            
    
    def ingest(self, input_dir: str):
        print("Ingestion: This can take time for uploading and ingesting the data into our database...")
        file_paths = glob.glob(os.path.join(input_dir, "*.pdf"))
        if not file_paths:
            raise Exception("No files submitted")
        file_resp, time = upload_multiple_files(file_paths, os.path.join(self.url, "ingest"), headers=self.headers, extra_data=self.init_req_body)
        check_response(file_resp)
        self.file_resp = file_resp.json()["message"]
        print(self.file_resp)
        print("Ingestion time:", time)
        
    def ingest_bytes(self, filenames: list, file_bytes: list):
        if not filenames and not file_bytes:
            raise Exception("No files submitted")
        file_resp, time = upload_multiple_files(filenames, os.path.join(self.url, "ingest"), headers=self.headers, extra_data=self.init_req_body, bytes_data=file_bytes)
        check_response(file_resp)
        self.file_resp = file_resp.json()["message"]
        print(self.file_resp)
        print("Ingestion time:", time)
        
    def query(self, query: str, num_seed_nodes: int = 1, chunk_only: bool = True, strategy: str = "graph_extended"):
        
        query_req_body = {
            "project_name": self.project_name,
            "query": query,
            "num_seed_nodes": num_seed_nodes,
            "chunk_only": chunk_only,
            "strategy": strategy
        }
        
        if not chunk_only:
            print("This could take some time as LLM generates the answer for the given query...")
        query_response, time = send_request(os.path.join(self.url, "query"), req_body=query_req_body, headers=self.headers)
        check_response(query_response)
        print("Query time:", time)
        
        return query_response.json()
    
    def end_session(self):
        session_response = delete_request(os.path.join(self.url, "end_session", self.project_name), headers=self.headers)
        check_response(session_response)
        session_status = session_response.json()["message"]
        print(session_status)
        
    @staticmethod
    def remove(url, project_name, api_token):
        print("Removing project from the server...")
        headers = {
            "Seqtra-token": api_token
        }
        resp = delete_request(os.path.join(url, "delete", project_name), headers)
        check_response(resp)
        
        return resp.json()["message"]
    
        
        