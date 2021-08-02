import pprint
import prefect
import pymongo
from prefect import task, Flow, Client
from prefect.run_configs import KubernetesRun
from prefect.storage import GitHub
from prefect.tasks.postgres.postgres import PostgresExecute, PostgresFetch

github_storage = GitHub(
    repo="kwrobert/sfl-skillshare",  # name of repo
    path="etl/prefect_hello_world_prod.py",  # location of flow file in repo
    # access_token_secret="GITHUB_ACCESS_TOKEN",  # name of personal access token secret
)


@task
def extract():
    logger = prefect.context.get("logger")
    logger.info("Hello from extract!")
    return "extract"


@task
def transform(users):
    logger = prefect.context.get("logger")
    logger.info(f"Hello from transform! I was given the following data:")
    pprint.pprint(f"{users}")
    return users + " transform"


@task
def load(users):
    logger = prefect.context.get("logger")
    logger.info(f"Hello from load! I was given {users}. I will now put it elsewhere")


with Flow("sfl-hello-world-prod") as flow:
    data = extract()
    transformed_data = transform(data)
    load(transformed_data)

# Register the flow under the "sfl" project
flow.run_config = KubernetesRun(
    labels=["sfl"],
    image="410118848099.dkr.ecr.us-east-1.amazonaws.com/prefect/custom-run-image",
)
flow.storage = github_storage
