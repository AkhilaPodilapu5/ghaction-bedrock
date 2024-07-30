REVIEW_MULTIVARPROMPT = """Human: 
You are a code generator. Your responsibility is to 
generate a GitHub Actions pipeline YAML based on the stages provided. The base OS for all jobs should be Ubuntu.

You will be given a list of stages :
- Use this list of stages: {stages} provided to generate the corresponding GitHub Actions pipeline YAML. The YAML should be well-formed and follow the best practices for GitHub Actions pipelines.
- Depending on the {applicationType} provided, generate the build phase accordingly.
- All actions use the latest stable versions.
- Paths and arguments are configured correctly.

Additionally, the pipeline should:
- Configure AWS credentials to interact with AWS services.
- Build a Docker image and push it to an Amazon ECR repository.

Make sure to include:
- A step to set up AWS CLI and configure AWS credentials.
- A step to log in to Amazon ECR.
- A step to build the Docker image.
- A step to tag the Docker image.
- A step to push the Docker image to the ECR repository.


Assistant: 
"""



REVIEW_PROMPT_OUTPUT_FORMAT = """
yaml
"""
