import json
import os
from omegaconf import OmegaConf
import streamlit as st
import datetime

from src.seqtra_client import SeqtraClient
from src.utils import visualize_graph
import uuid

req_cfg = OmegaConf.load("./config/request.yaml")
st.set_page_config(layout="wide")
cols = st.columns([0.9, 0.1])
cols[1].button("Clear", type="primary", use_container_width=True)
st.write("# Welcome to Seqtra! 👋")
st.write("Read our documentation at: https://github.com/seqtra/SeqtraClient")
st.write("Generate Seqtra API keys at https://app.seqtra.com/")

try:
    with st.sidebar:
        st.write("## Set up all options properly before submitting ")
        uploaded_files = st.file_uploader("Choose files to upload", type="pdf", accept_multiple_files=True, help="Please note that we have 100 total page (single or multiple PDFs) limit currently.")
        filenames = []
        file_bytes = []
        if uploaded_files:
            for uploaded_file in uploaded_files:
                bytes_data = uploaded_file.read()
                filenames.append(uploaded_file.name)
                file_bytes.append(bytes_data)
            
        st.session_state.is_llm_disabled = True
        api_token = st.text_input("Seqtra API key: ", req_cfg.api_token, help="Please generate API keys at https://app.seqtra.com/")
        project_name = st.text_input("Project Name:", req_cfg.project_name, help="Project name for your current file collection.  Make sure to change this in order to not mix up your personal files with already existing test file or to segregate the knowledge base according to data or application domain. This will also avoid unintentionally reducing the page limit available.")
        chunk_opt = st.selectbox("Chunk Only?", options=["True", "False"], help="If true, LLM is not used to generate chunk summary")
        chunk_opt = True if chunk_opt == "True" else False
        if not chunk_opt:
            st.session_state.is_llm_disabled = False
        llm_opt = st.selectbox("Choose your LLM:", options=["claude", "openai"], help="Only two options available at the moment", disabled=st.session_state.is_llm_disabled)
        llm_token = st.text_input(f"Your {llm_opt} API Key:", req_cfg.llm_key, disabled=st.session_state.is_llm_disabled)
        num_seed_nodes = st.number_input("Number of seed nodes:", min_value=1, max_value=20, value=req_cfg.num_seed_nodes, help="This is equivalent to topk parameter in RAG. It is named so in our service, due to the presence of graph linkages and traversal during chunking and retrieval. You may optimize this for your use case.")
        strategy = st.selectbox("Select your retrieval strategy: ", options=["seed_only", "seed_extended", "graph", "graph_extended",], index=3, help="For more details, check Readme.")
        if not strategy:
            raise Exception("Select one of the available strategies")
        st.session_state.ingested = False
        st.markdown("Delete Project: ", help="It will delete files uploaded previously along with associated graphs. When uploading new documents not associated with previous project, please delete project or create new project.")
        if st.button("Delete", type="primary", help="It will delete files uploaded previously along with associated graphs. When uploading new documents not associated with previous project, please delete project or create new project."):
            message = SeqtraClient.remove(url=req_cfg.url, project_name=project_name, api_token=api_token)
            st.success(message)
    query = st.text_area("Your Query:", placeholder="Enter your query here..")
    if st.button("Submit", type="primary"):
        if not filenames:
            raise Exception("No Files uploaded")
        with st.spinner("Ingestion: This can take time for uploading and ingesting the data into our database...", show_time=True):
            seqtra = SeqtraClient(
                api_token=api_token, project_name=project_name, url=req_cfg.url,
                llm=llm_opt, llm_key=llm_token
            )
            st.success(seqtra.init_status)
            seqtra.ingest_bytes(filenames, file_bytes)
            st.success(seqtra.file_resp)
        if not chunk_opt:
            with st.spinner("This could take some time as LLM generates the answer for the given query...", show_time=True):
                query_resp = seqtra.query(
                    query = query, 
                    num_seed_nodes = num_seed_nodes,
                    chunk_only = chunk_opt, 
                    strategy = strategy
                )
        else:
            query_resp = seqtra.query(
                query = query, 
                num_seed_nodes = num_seed_nodes,
                chunk_only = chunk_opt, 
                strategy = strategy
            )
        graph = query_resp["graph"]
        if query_resp["answer"]:
            with st.chat_message("assistant"):
                st.markdown(query_resp["answer"])
        st.write("### Visualization of Chunks relevant to the Query")
        visualize_graph(graph, query_resp["chunks"])
        seqtra.end_session()
except Exception as e:
    st.error(str(e))