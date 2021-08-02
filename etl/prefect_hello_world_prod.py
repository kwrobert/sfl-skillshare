import pprint
import prefect
from prefect import task, Flow, Client
from prefect.run_configs import UniversalRun
from prefect.storage import GitHub

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
flow.run_config = UniversalRun(labels=["sfl"])
flow.storage = github_storage
