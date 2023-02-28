#!/bin/env python

import sys
import argparse
import csv
import requests
from BsJson import BsJson, BsJsonSection

##################################################################################################

"""
This script generates routing and authority statements for Webcert. 
It can generate a JSON file for NTJP-PROD and RTP-PROD. 

The logic to create the actual JSON file can be found in BsJson.py.
"""


##################################################################################################
def printerr(text):
    """Print to stderror"""

    print(text, file=sys.stderr)

##################################################################################################
#                                 Main Program
##################################################################################################
# Set up global variables
# Definition of producer information related to the two targets; NTJP-PROD and RTP-PROD
PRODUCER_HSA_ID = {
    "NTJP-PROD": "SE5565594230-B8N"
}

PRODUCER_DESCRIPTION = {
    "NTJP-PROD": "Inera AB -- Intygstjänster -- Webcert"
}

# Both producers have one single URL which is used for all three contracts
PRODUCER_URL = {
    "NTJP-PROD": {
        "urn:riv:clinicalprocess:healthcond:certificate:SendMessageToCareResponder:2":
            "https://webcert.ntjp.intygstjanster.se/services/send-message-to-care/v2.0"
    }
}

# Definition of the three request contracts (the same for all target plattforms)
SERVICE_CONTRACTS = [
    {
        "namnrymd": "urn:riv:clinicalprocess:healthcond:certificate:SendMessageToCareResponder:2",
        "beskrivning": "SendMessageToCare",
        "majorVersion": 2
    }
]

##################################################################################################
# Parse arguments
parser = argparse.ArgumentParser()

parser.add_argument("filename", nargs=1, help="name of CSV file")
args = parser.parse_args()

TARGET_TP = "NTJP-PROD"

CSV_FILE = args.filename[0]

##################################################################################################
# And the action

# BsJsonSection is defined in BsJson.py
include_section = BsJsonSection()

# Add the contracts to the include section
for contract in SERVICE_CONTRACTS:
    include_section.add_contract(contract["namnrymd"], contract["beskrivning"])

with open(CSV_FILE, encoding='utf-8-sig') as csv_file:
    # Read and parse all rows in the CSV file
    csv_reader = csv.reader(csv_file, delimiter=';')

    for row in csv_reader:
        la_hsaid = row[0].strip()  # Pick up from file
        la_description = row[1].strip()  # Pick up from file

        include_section.add_logicalAddress(la_hsaid, la_description)

        # Add a routing (vagval) statement for each of the three contracts
        for contract in SERVICE_CONTRACTS:
            include_section.add_routing(PRODUCER_HSA_ID[TARGET_TP],
                                        PRODUCER_URL[TARGET_TP][contract["namnrymd"]],
                                        la_hsaid,
                                        contract["namnrymd"]
                                        )
            include_section.add_authorization("SE5565594230-B31",
                                              la_hsaid,
                                              contract["namnrymd"]
                                              )

# BsJson is defined in BsJson.py
content = BsJson(TARGET_TP)
content.add_section("include", include_section)

# The output JSON is written to stdout
content.print_json()

exit()
