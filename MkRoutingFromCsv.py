#!/bin/env python

import sys
import argparse
import csv
import requests
from BsJson import BsJson, BsJsonSection

##################################################################################################

"""
This script reads logical addresses from a CSV file and create BS JSON with routing statements
for the three request contracts. It can generate a JSON file for NTJP-PROD and RTP-PROD. 

The logic to create the actual JSON file can be found in BsJson.py.
"""


##################################################################################################
def printerr(text):
    """Print to stderror"""

    print(text, file=sys.stderr)


def get_la_from_takaip():
    """This function reads the TAK-api and creates a dict with all logical addresses. The actual LA is used as key.

    LA descriptions are read from all TAKs. There is a priority order, where NTJP-PROD have the highest rank, followed by
    RTP-PROD and so on.
    The reason for this is that a CSV list of units (logical addresses) from TakeCare truncate the unit name after 25
    characters. We do not want to use those truncated names if the LA is already defined in a TAK. The user of this
    script can control this behaviour with the "-r" flag.
    """

    # Ensure order to get LA from TP with highest rank
    ntjp_prod_id = 4
    rtp_prod_id = 5
    ntjp_qa_id = 6
    rtp_qa_id = 7
    # Define priority order
    tp_ids = [ntjp_prod_id, rtp_prod_id, ntjp_qa_id, rtp_qa_id]

    logical_address_descriptions = {}

    # Obtain all LA for one TAK at the time and store in the dict
    for tp_id in tp_ids:
        response = requests.get(f"http://api.ntjp.se/coop/api/v1/logicalAddresss?connectionPointId={tp_id}")
        for la in response.json():
            la_id = la["logicalAddress"]
            la_desc = la["description"]
            if la_id not in logical_address_descriptions:
                logical_address_descriptions[la_id] = la_desc

    return logical_address_descriptions


##################################################################################################
#                                 Main Program
##################################################################################################
# Set up global variables
# Definition of producer information related to the two targets; NTJP-PROD and RTP-PROD
PRODUCER_HSA_ID = {
    "RTP-PROD": "SE2321000016-F835",
    "NTJP-PROD": "SE2321000016-FH3P"
}

PRODUCER_DESCRIPTION = {
    "RTP-PROD": "Region Stockholm -- EDI som tjänsteproducent -- Ny tjänsteproducent fr o m 2021-10-12, har ersatt tidigare producent ""...4HR3"".",
    "NTJP-PROD": "Region Stockholm -- Tjänsteplattform som tjänsteproducent -- Tjänsteproducent fr o m 2021-09-22, ersätter ""...-7P35"" som producent!"
}

# Both producers have one single URL which is used for all three contracts
PRODUCER_URL = {
    "RTP-PROD": {
        "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1":
            "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
        "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1":
            "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
        "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1":
            "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21"
    },
    "NTJP-PROD": {
        "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1":
            "https://rtp.prod.internet.regionstockholm.se/vp/clinicalprocess/activity/request/ProcessRequest/1",
        "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1":
            "https://rtp.prod.internet.regionstockholm.se/vp/clinicalprocess/activity/request/ProcessRequestConfirmation/1",
        "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1":
            "https://rtp.prod.internet.regionstockholm.se/vp/clinicalprocess/activity/request/ProcessRequestOutcome/1"
    }
}

# Definition of the three request contracts (the same for all target plattforms)
SERVICE_CONTRACTS = [
    {
        "namnrymd": "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
        "beskrivning": "Submission of a request to a healtcare facility",
        "majorVersion": 1
    },
    {
        "namnrymd": "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
        "beskrivning": "Submission of a request to a healtcare facility",
        "majorVersion": 1
    },
    {
        "namnrymd": "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1",
        "beskrivning": "Submission of a request to a healtcare facility",
        "majorVersion": 1
    },
]

##################################################################################################
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--replace", action='store_true',
                    help="replace logical address descriptions from TAK-api")
parser.add_argument("-t", "--target", action='store', type=str, required=True,
                    help="target must be one of NTJP-PROD or RTP-PROD")
parser.add_argument("filename", nargs=1, help="name of CSV file")
args = parser.parse_args()

REPLACE_LA_DESCRIPTION = args.replace
TARGET_TP = args.target.upper()

if not (TARGET_TP == "NTJP-PROD" or TARGET_TP =="RTP-PROD"):
    parser.print_help()
    exit(1)

CSV_FILE = args.filename[0]

##################################################################################################
# And the action

logical_address_descriptions = {}

# If the user specifies -r then we need to obtain all descriptions of all LA from the TAK-api
if REPLACE_LA_DESCRIPTION:
    logical_address_descriptions = get_la_from_takaip()

# BsJsonSection is defined in BsJson.py
include_section = BsJsonSection()

# Add the contracts to the include section
for contract in SERVICE_CONTRACTS:
    include_section.add_contract(contract["namnrymd"], contract["beskrivning"])

with open(CSV_FILE) as csv_file:
    # Read and parse all rows in the CSV file
    csv_reader = csv.reader(csv_file, delimiter=';')

    for row in csv_reader:
        la_hsaid = row[0].strip()  # Pick up from file
        la_description = row[1].strip()  # Pick up from file

        # Replace the description with the one from the TAK, if it exist
        if la_hsaid in logical_address_descriptions:
            la_description = logical_address_descriptions[la_hsaid]

        include_section.add_logicalAddress(la_hsaid, la_description)

        # Add a routing (vagval) statement for each of the three contracts
        for contract in SERVICE_CONTRACTS:
            include_section.add_routing(PRODUCER_HSA_ID[TARGET_TP],
                                        PRODUCER_URL[TARGET_TP][contract["namnrymd"]],
                                        la_hsaid,
                                        contract["namnrymd"]
                                        )

# BsJson is defined in BsJson.py
content = BsJson(TARGET_TP)
content.add_section("include", include_section)

# The output JSON is written to stdout
content.print_json()

exit()
