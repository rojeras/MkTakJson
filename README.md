# bs-json
Generate BS JSON files 

## Install
1. Clone this repo
1. Use python3
1. Install the python python request module. It is a good idea to use a python virtual environment.

    `pip3 install requests`

## Use
1. Download the input file from Ineras TAK-api:

    `curl -X GET "http://api.ntjp.se/coop/api/v1/serviceProductions?include=connectionPoint,logicalAddress,serviceContract,serviceProducer,physicalAddress" -H "accept: application/json" > prods.json`

1. Run program with parameter `-h` to see required parameters.

