#!/bin/sh 

# This script will fetch production (vägval) information from the TAK-api and print.
# Dumped to a file it is used as input to the RequestReReoute.py script.

curl -X GET "http://api.ntjp.se/coop/api/v1/serviceProductions?include=connectionPoint,logicalAddress,serviceContract,serviceProducer,physicalAddress" -H "accept: application/json" 

