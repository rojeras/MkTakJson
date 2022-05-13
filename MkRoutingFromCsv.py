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


    # print(json.dumps(update_include, ensure_ascii=False))
    # print("here is your checkmark: " + u'\u2713');

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


def get_producer_url(producer, envir, namespace):

    key = f"{producer}-{envir}"

    ix = -1
    if (namespace == "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1"):
        ix = 0
    elif (namespace == "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1"):
        ix = 1
    elif (namespace == "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1"):
        ix = 2

    return PRODUCER_URL[key][ix]

##################################################################################################


def create_sample_files(target_tp, target_envir, phase):

    printerr(f"Sample {phase} file for {target_tp}-{target_envir} \n")

    body = get_header(target_tp, target_envir)

    if (phase == "UPDATE"):
        include = {}
        include["tjanstekontrakt"] = get_json_contracts()
        include["tjanstekomponenter"] = get_sample_service_components()
        include["logiskadresser"] = get_sample_logical_addresses()
        include["vagval"] = get_sample_routes()

        body["inkludera"] = include

    elif (phase == "REMOVE"):
        exclude = {}
        # exclude["tjanstekontrakt"] = get_json_contracts()
        # exclude["tjanstekomponenter"] = get_sample_service_components()
        # exclude["logiskadresser"] = get_sample_logical_addresses()
        exclude["vagval"] = get_sample_routes()

        body["exkludera"] = exclude

    json_body = json.dumps(body)
    print(json_body)

##################################################################################################


def get_sample_logical_addresses():

    return [
        {
            "hsaId": "FEJK-MOTTAGNING-SLL-HSA-ID",
            "beskrivning": "FEJK-MOTTAGNING-SLL"
        }
    ]

##################################################################################################


def get_sample_service_components():

    return [
        {
            "hsaId": "SE2321000016-XXXX",
            "beskrivning": "Region Stockholm -- FEJK -- Remissystem"
        }
    ]

##################################################################################################


def get_sample_routes():

    return [
        {
            "adress": "https://test-api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
            "logiskAdress": "FEJK-MOTTAGNING-SLL-HSA-ID",
            "tjanstekontrakt": "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
            "rivtaprofil": "RIVTABP21",
            "tjanstekomponent": "SE2321000016-XXXX"
        },
        {
            "adress": "https://test-api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
            "logiskAdress": "FEJK-MOTTAGNING-SLL-HSA-ID",
            "tjanstekontrakt": "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
            "rivtaprofil": "RIVTABP21",
            "tjanstekomponent": "SE2321000016-XXXX"
        },
        {
            "adress": "https://test-api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
            "logiskAdress": "FEJK-MOTTAGNING-SLL-HSA-ID",
            "tjanstekontrakt": "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1",
            "rivtaprofil": "RIVTABP21",
            "tjanstekomponent": "SE2321000016-XXXX"
        }
    ]

##################################################################################################


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
