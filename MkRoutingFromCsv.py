import sys
import argparse
import csv
from BsJson import BsJson, BsJsonSection

##################################################################################################

"""
This script reads logical addresses from a CSV file and create BS Json with routing statements
for the three request contracts. 
It is only expected to be used for SLL-PROD.
"""


##################################################################################################
def printerr(text):
    print(text, file=sys.stderr)


##################################################################################################
#                                 Main Program
##################################################################################################
# Parse arguments
parser = argparse.ArgumentParser()
# parser.add_argument("filename", nargs=1, type=argparse.FileType('r'))
parser.add_argument("filename", nargs=1)
args = parser.parse_args()

CSV_FILE = args.filename[0]

##################################################################################################
# Set up global variables

PRODUCER_HSA_ID = "SE2321000016-F835"
PRODUCER_DESCRIPTION = "Region Stockholm -- EDI som tjänsteproducent -- Ny tjänsteproducent fr o m 2021-10-12, har ersatt tidigare producent ""...4HR3""."
PRODUCER_URL = "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21"

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

include_section = BsJsonSection()

for contract in SERVICE_CONTRACTS:
    include_section.add_contract(contract["namnrymd"], contract["beskrivning"])

with open(CSV_FILE) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')

    for row in csv_reader:
        la_hsaid = row[0].strip()  # Pick up from file
        la_description = row[1].strip()  # Pick up from file

        include_section.add_logicalAddress(la_hsaid, la_description)

        for contract in SERVICE_CONTRACTS:
            include_section.add_routing(PRODUCER_HSA_ID,
                                        PRODUCER_URL,
                                        la_hsaid,
                                        contract["namnrymd"]
                                        )

content = BsJson("SLL-PROD")
content.add_section("include", include_section)
content.print_json()

exit()
