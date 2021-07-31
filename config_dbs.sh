#!/bin/bash

# Configure postgres DB, tables, and 
export PGPASSWORD="postgres"
createdb -h localhost -p 5432 -U postgres sfl
psql -h localhost -p 5432 -U postgres -d sfl -f postgres.sql

