# Set this name to the name of your last Helm release
NAME=prefect-server
# Choose a version to upgrade to or omit the flag to use the latest version
# VERSION=2021.03.06

# helm upgrade $NAME prefecthq/prefect-server --version $VERSION
helm upgrade $NAME .
