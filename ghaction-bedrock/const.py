import os
JSON_SEARH_PATTERN = r'```json([\s\S]*?)```'
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID',"anthropic.claude-v2")
REGION = os.getenv('REGION','us-east-1')