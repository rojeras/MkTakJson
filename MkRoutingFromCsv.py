from datetime import datetime
import sys
import argparse
import json
import csv
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


def get_header():

    plattform = "SLL-PROD"
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0100")

    return {
        "plattform": plattform,
        "formatVersion": "1.0",
        "version": "1",
        "bestallningsTidpunkt": now,
        "utforare": "Region Stockholm - Forvaltningsobjekt Informationsinfrastruktur",
        "genomforandeTidpunkt": now,
    }

##################################################################################################


def create_json_file() -> None:
    """Will create json file"""

    include = {}
    vagval = []
    logiskaAdresser = []

    with open(CSV_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:

            la_hsaid = row[0].strip()            # Pick up from file
            la_description = row[1].strip()  # Pick up from file

            logiskAdress = {
                "hsaId": la_hsaid,
                "beskrivning": la_description
            }
            # if (logiskAdress not in logiskaAdresser):
            logiskaAdresser.append(logiskAdress)

            vagval.append({
                "tjanstekomponent": PRODUCER_HSA_ID,
                "adress": PRODUCER_URL,
                "logiskAdress": la_hsaid,
                "tjanstekontrakt": SERVICE_CONTRACT_NAMESPACE["ProcessRequest"],
                "rivtaprofil": "RIVTABP21"
            })
            vagval.append({
                "tjanstekomponent": PRODUCER_HSA_ID,
                "adress": PRODUCER_URL,
                "logiskAdress": la_hsaid,
                "tjanstekontrakt": SERVICE_CONTRACT_NAMESPACE["ProcessRequestConfirmation"],
                "rivtaprofil": "RIVTABP21"
            })
            vagval.append({
                "tjanstekomponent": PRODUCER_HSA_ID,
                "adress": PRODUCER_URL,
                "logiskAdress": la_hsaid,
                "tjanstekontrakt": SERVICE_CONTRACT_NAMESPACE["ProcessRequestOutcome"],
                "rivtaprofil": "RIVTABP21"
            })

    # Combine the information
    include["tjanstekontrakt"] = get_json_contracts()

    include["logiskadresser"] = logiskaAdresser

    include["vagval"] = vagval

    # Print out the JSON data
    content = get_header()
    content["inkludera"] = include

    printerr(f"Generating UPDATE file")
    print(json.dumps(content, ensure_ascii=False, indent=4))


##################################################################################################


def get_json_contracts():

    return [
        {
            "namnrymd": "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
            "beskrivning": "Submission of a request to a healtcare facility",
            "majorVersion": 1
        },
        {
            "namnrymd": "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1",
            "beskrivning": "Submission of a request to a healtcare facility",
            "majorVersion": 1
        },
        {
            "namnrymd": "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
            "beskrivning": "Submission of a request to a healtcare facility",
            "majorVersion": 1
        }
    ]


##################################################################################################
#                                 Main Program
##################################################################################################
# Parse arguments
parser = argparse.ArgumentParser()
#parser.add_argument("filename", nargs=1, type=argparse.FileType('r'))
parser.add_argument("filename", nargs=1)
args = parser.parse_args()

CSV_FILE = args.filename[0]

##################################################################################################
# Set up global variables

PRODUCER_HSA_ID = "SE2321000016-F835"
PRODUCER_DESCRIPTION = "Region Stockholm -- EDI som tjänsteproducent -- Ny tjänsteproducent fr o m 2021-10-12, har ersatt tidigare producent ""...4HR3""."
PRODUCER_URL = "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21"

SERVICE_CONTRACT_NAMESPACE = {
    "ProcessRequest": "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
    "ProcessRequestConfirmation": "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
    "ProcessRequestOutcome": "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1"
}

##################################################################################################
# Main program switch

create_json_file()

exit()
