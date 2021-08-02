import pprint
import pymongo
import prefect
from prefect import task, Flow, Client
from prefect.run_configs import KubernetesRun
from prefect.storage import GitHub
from prefect.tasks.postgres.postgres import PostgresExecute, PostgresFetch

github_storage = GitHub(
    repo="kwrobert/sfl-skillshare",  # name of repo
    path="etl/etl_prod.py",  # location of flow file in repo
    access_token_secret="GITHUB_ACCESS_TOKEN",  # name of personal access token secret
)

# task_pg_get_all_users = PostgresExecute(
#     db_name="sfl",
#     host="localhost",
#     port=5433,
#     user="postgres",
#     query="SELECT * FROM users",
# )
task_pg_get_all_users_with_friends_as_json = PostgresFetch(
    db_name="sfl",
    host="postgres.default.svc.cluster.local",
    # Don't want to conflict with Prefect Postgres
    port=5433,
    user="postgres",
    query="""
WITH 
friends AS (
  SELECT user_id, friend_id 
  FROM friends
),
users AS (
  SELECT u.*,
         json_agg(f) AS friends
  FROM users u
  JOIN friends f
  ON u.id = user_id
  GROUP BY u.id 
)
SELECT json_agg(users)
FROM users;
    """,
    # "SELECT u.*, f.friend_id FROM users as u INNER JOIN friends as f ON u.id = # f.user_id",
    fetch="all",
)


@task
def extract():
    logger = prefect.context.get("logger")
    logger.info("Hello from extract!")
    rows = task_pg_get_all_users_with_friends_as_json.run(password="postgres")
    pprint.pprint(rows[0][0])
    return rows[0][0]


@task
def transform(users):
    logger = prefect.context.get("logger")
    logger.info(f"Hello from transform! I was given the following data:")
    pprint.pprint(f"{users[0]}")
    for user in users:
        friend_usernames = []
        for friend in user["friends"]:
            friend_usernames += [
                d["username"] for d in users if d["id"] == friend["friend_id"]
            ]
        user["friends"] = friend_usernames
        pprint.pprint(user)

    return users


@task
def load(users):
    logger = prefect.context.get("logger")
    logger.info(f"Hello from load! I was given {users}. I will now put it elsewhere")
    client = pymongo.MongoClient("mongodb://root:example@mongo.default.svc.cluster.local:27017/")
    db = client.sfl
    db.users.insert_many(users)



with Flow("sfl-etl-pg-to-mongo") as flow:
    data = extract()
    transformed_data = transform(data)
    load(transformed_data)

flow.run_config = KubernetesRun(
    labels=["sfl"],
    image="410118848099.dkr.ecr.us-east-1.amazonaws.com/prefect/custom-run-image:latest",
)
flow.storage = github_storage
