#/bin/bash

# Just port forwards all the DB pods so I can load data
kubectl port-forward svc/mongo 27017:27017 &
kubectl port-forward svc/postgres 5433:5433 &
kubectl port-forward svc/neo4j 7687:7687 &
kubectl port-forward svc/prefect-server-apollo 4200:4200 &
kubectl port-forward svc/prefect-server-ui 8080:8080 &
