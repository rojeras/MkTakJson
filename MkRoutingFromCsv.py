from datetime import datetime
import sys
import argparse
import json
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
"""
class BsJson:
    def __init__(self, plattform, executor="Region Stockholm - Forvaltningsobjekt Informationsinfrastruktur"):
        self.plattform = plattform
        self.executor = executor
        self.include = None
        self.exclude = None

    def add_section(self, type, section):

        if type == "include":
            self.include = section
        elif type == "exclude":
            self.exclude = section
        else:
            printerr(f"add_section called with unknown type: {type}")
            exit(1)

    def get_headerx(self):
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0100")

        return {
            "plattform": self.plattform,
            "formatVersion": "1.0",
            "version": "1",
            "bestallningsTidpunkt": now,
            "utforare": self.executor,
            "genomforandeTidpunkt": now,
        }

    def print_json(self):

        content = self.get_headerx()
        if self.include:
            content["inkludera"] = BsJsonSection.get_json(self.include)
        if self.exclude:
            content["exkludera"] = BsJsonSection.get_json(self.exclude)

        printerr(f"Generating UPDATE file")
        print(json.dumps(content, ensure_ascii=False, indent=4))


class BsJsonSection:
    def __init__(self):
        self.logicalAddresses = []
        self.components = []
        self.contracts = []
        self.routings = []
        self.authorities = []

    def add_logicalAddress(self,
                           id,
                           description):

        logicalAddress = {
            "hsaId": id,
            "beskrivning": description
        }

        if logicalAddress not in self.logicalAddresses:
            self.logicalAddresses.append(logicalAddress)

    def add_component(self, id, description):

        component = {
            "hsaId": id,
            "beskrivning": description
        }

        if component not in self.components:
            self.components.append(component)

    def add_contract(self,
                     namespace,
                     description):

        ix = namespace.rfind(":") + 1
        majorStr = namespace[ix:]
        major = int(majorStr)

        contract = {
            "namnrymd": namespace,
            "beskrivning": description,
            "majorVersion": major
        }

        if contract not in self.contracts:
            self.contracts.append(contract)

    def add_routing(self,
                    component,
                    address,
                    logicalAddress,
                    namespace,
                    rivtaProfile="RIVTABP21"):

        routing = {
            "tjanstekomponent": component,
            "adress": address,
            "logiskAdress": logicalAddress,
            "tjanstekontrakt": namespace,
            "rivtaprofil": rivtaProfile
        }
        if routing not in self.routings:
            self.routings.append(routing)

    def get_json(self):

        return {
            "tjanstekontrakt": self.contracts,
            "tjanstekomponenter": self.components,
            "logiskadresser": self.logicalAddresses,
            "anropsbehorigheter": self.authorities,
            "vagval": self.routings,
        }

"""



##################################################################################################

def create_json_file() -> None:
    """Will create json file"""

    include_section = BsJsonSection()

    for contract in get_json_contracts():
        include_section.add_contract(contract["namnrymd"], contract["beskrivning"])

    with open(CSV_FILE) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=';')

        for row in csv_reader:
            la_hsaid = row[0].strip()  # Pick up from file
            la_description = row[1].strip()  # Pick up from file

            include_section.add_logicalAddress(la_hsaid, la_description)
            include_section.add_routing(PRODUCER_HSA_ID,
                                        PRODUCER_URL,
                                        la_hsaid,
                                        SERVICE_CONTRACT_NAMESPACE["ProcessRequest"]
                                        )
            include_section.add_routing(PRODUCER_HSA_ID,
                                        PRODUCER_URL,
                                        la_hsaid,
                                        SERVICE_CONTRACT_NAMESPACE["ProcessRequestConfirmation"]
                                        )
            include_section.add_routing(PRODUCER_HSA_ID,
                                        PRODUCER_URL,
                                        la_hsaid,
                                        SERVICE_CONTRACT_NAMESPACE["ProcessRequestOutcome"]
                                        )
    content = BsJson("TEST-TP")
    content.add_section("include", include_section)
    content.print_json()

def xxxcreate_json_file() -> None:
    """Will create json file"""

    include = {}
    vagval = []
    logiskaAdresser = []

    with open(CSV_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            la_hsaid = row[0].strip()  # Pick up from file
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
# parser.add_argument("filename", nargs=1, type=argparse.FileType('r'))
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
