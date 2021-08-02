#!/bin/bash

# Configure postgres DB, tables, and 
export PGPASSWORD="postgres"
createdb -h localhost -p 5433 -U postgres sfl
psql -h localhost -p 5433 -U postgres -d sfl -f postgres.sql

# Setup prefect data piplineing tool
# prefect server create-tenant --name sfl --slug sfl
# prefect create project "sfl"

