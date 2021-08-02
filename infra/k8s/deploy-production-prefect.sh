# The kubernetes namespace to install into, can be anything or excluded to install in the default namespace
NAMESPACE=prefect-server
# The Helm "release" name, can be anything but we recommend matching the chart name
NAME=prefect-server
# The path to your config that overrides values in `values.yaml`
CONFIG_PATH=./values.yaml
# The chart version to install
# VERSION=2021.03.06

helm install \
    --values $CONFIG_PATH \
    $NAME \
    prefecthq/prefect-server
    # ./helm/prefect-server
