from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import os
import boto3
import json
from botocore.client import Config
from langchain import PromptTemplate
from langchain.llms.bedrock import Bedrock
import re

from prompt import REVIEW_MULTIVARPROMPT, REVIEW_PROMPT_OUTPUT_FORMAT
from const import *
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import base64
from urllib.parse import urlparse


app = FastAPI()

region = REGION
config = Config(read_timeout=600, retries={'max_attempts': 0})
json_regex = JSON_SEARH_PATTERN
def get_bedrock_client(region):
    return boto3.client("bedrock-runtime", region_name=region, config=config)

def create_bedrock_llm(bedrock_client, model_version_id):
    return Bedrock(
        model_id=model_version_id, 
        client=bedrock_client,
        model_kwargs={'max_tokens_to_sample': 8000, 'temperature': 0.0, 'top_k': 250, 'top_p': 0.999, 'stop_sequences': ['Human:']}
    )

model_version_id = BEDROCK_MODEL_ID
cl_llm = create_bedrock_llm(get_bedrock_client(region), model_version_id)

review_multi_var_prompt = PromptTemplate(
    input_variables=["stages", "applicationType"], 
    template=REVIEW_MULTIVARPROMPT
)
review_output_format = REVIEW_PROMPT_OUTPUT_FORMAT

def parse_repo_url(repo_url: str):
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) != 2:
        raise ValueError("Invalid repository URL format")
    owner, repo = path_parts
    return owner, repo

@app.post("/create-file/")
async def create_file(
    repo_url: str = Query(..., description="provide github url to create or update file"),
    branch: str = Query(..., description="provide branch name to create or update file"),
    commit_message: str = Query(..., description="provide commit message to create or update file"),
    github_token: str = Query(..., description="provide github token to create or update file"),
    stages: str = Query(..., description="provide stages that should be included in pipeline"),
    applicationTechnology: str = Query(..., description="provide application type"),
    file_name: str = Query(..., description="provide file name to create or update")
) -> JSONResponse:
    try:
        prompt = review_multi_var_prompt.format(stages=stages, applicationType=applicationTechnology, format=review_output_format)
        
        # Debug: Print the prompt to ensure it's formatted correctly
        #print(f"Generated Prompt: {prompt}")
        
        # Request the solution from Bedrock
        
        solution = cl_llm(prompt)
        
        #print(f"raw response is: {solution}")
        yaml_pattern = r"```yaml\n(.*?)\n```"

        match = re.search(yaml_pattern, solution, re.DOTALL)

        if match:
            result = match.group(1)
            print(result)
        else:
            print("No YAML content found in the response.")
        file_content = result
        owner, repo = parse_repo_url(repo_url)
        file_path = f".github/workflows/{file_name}.yaml"
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        #Check if the file exists
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            # File exists, update it
            file_info = response.json()
            sha = file_info['sha']
        elif response.status_code == 404:
            # File does not exist, no SHA needed
            sha = None
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to access the file")

        # Encode the content to base64
        content_base64 = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')

        data = {
            "message": commit_message,
            "content": content_base64,
            "branch": branch,
            "sha": sha
            
        }

        response = requests.put(api_url, headers=headers, json=data)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")
        # try:
        #     if response.status_code in [200, 201]:
        return JSONResponse(content=response.content)
        # except Exception as e:
        #     print(f"Error occurred: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))