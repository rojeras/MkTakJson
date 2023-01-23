import sys
import argparse
import csv
import requests
from BsJson import BsJson, BsJsonSection

##################################################################################################

"""
This script reads logical addresses from a CSV file and create BS Json with routing statements
for the three request contracts. 
It is currently expected to be used for SLL-PROD.
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

    logical_addess_descriptions = {}

    # Obtain all LA for one TAK at the time and store in the dict
    for tp_id in tp_ids:
        response = requests.get(f"http://api.ntjp.se/coop/api/v1/logicalAddresss?connectionPointId={tp_id}")
        for la in response.json():
            la_id = la["logicalAddress"]
            la_desc = la["description"]
            if la_id not in logical_addess_descriptions:
                logical_addess_descriptions[la_id] = la_desc

    return logical_addess_descriptions


##################################################################################################
#                                 Main Program
##################################################################################################
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--replace", action='store_true',
                    help="replace logical address descriptions from TAK-api")
parser.add_argument("filename", nargs=1)
args = parser.parse_args()

REPLACE_LA_DESCRIPTION = args.replace
CSV_FILE = args.filename[0]

##################################################################################################
# Set up global variables
# The current implementation presumes that all generated routing is for RTP-PROD and points to TakeCare (via EDI)
PRODUCER_HSA_ID = "SE2321000016-F835"
PRODUCER_DESCRIPTION = "Region Stockholm -- EDI som tjänsteproducent -- Ny tjänsteproducent fr o m 2021-10-12, har ersatt tidigare producent ""...4HR3""."
PRODUCER_URL = "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21"

# Definition of the three request contracts
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
            include_section.add_routing(PRODUCER_HSA_ID,
                                        PRODUCER_URL,
                                        la_hsaid,
                                        contract["namnrymd"]
                                        )

# BsJson is defined in BsJson.py
content = BsJson("SLL-PROD")
content.add_section("include", include_section)
# The output JSON is written to stdout
content.print_json()

exit()
