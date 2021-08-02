FROM 410118848099.dkr.ecr.us-east-1.amazonaws.com/prefecthq/prefect:latest

RUN pip install pymongo
RUN pip install --upgrade prefect[postgres]
# This config.toml file isn't in VC because it contains sensitive data
# IT just needs the following contents:
# [context.secrets]
# GITHUB_ACCESS_TOKEN = "<your token here>"
COPY ./config.toml /root/.prefect/ 

