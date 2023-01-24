#!/bin/sh 


curl -X GET "http://api.ntjp.se/coop/api/v1/serviceProductions?include=connectionPoint,logicalAddress,serviceContract,serviceProducer,physicalAddress" -H "accept: application/json" 

