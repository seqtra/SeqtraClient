import datetime
import os
import json
from omegaconf import OmegaConf

from src.seqtra_client import SeqtraClient
    
req_cfg = OmegaConf.load("./config/request.yaml")
os.makedirs("results", exist_ok=True)
seqtra = SeqtraClient(
    api_token=req_cfg.api_token, project_name=req_cfg.project_name, url=req_cfg.url,
    llm=req_cfg.llm, llm_key=req_cfg.llm_key
)
seqtra.ingest(req_cfg.file_dir)

query_resp = seqtra.query(
    query = req_cfg.query, 
    num_seed_nodes = req_cfg.num_seed_nodes,
    chunk_only = req_cfg.chunk_only, 
    strategy = req_cfg.strategy
)

save_file =  f"results/resp_{req_cfg.strategy}_{datetime.datetime.now()}.json"

with open(save_file, "w") as fp:
    json.dump(query_resp, fp)
    
print(f"Response saved to {save_file}")

# To delete use the following line of code
#SeqtraClient.remove(url=req_cfg.url, project_name=req_cfg.project_name, api_token=req_cfg.api_token)

    