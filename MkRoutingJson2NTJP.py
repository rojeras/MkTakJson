from email import parser
from random import sample
from datetime import datetime
import sys
import requests
import argparse
import json


##################################################################################################
def printerr(text):
    print(text, file=sys.stderr)

##################################################################################################


def get_header(target_tp, target_envir):

    plattform = f'{target_tp}-{target_envir}'

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


def get_connection_point_id(envir):
    """Get the connectionPointId of the RTP-QA|PROD"""

    response = requests.get(f"{TAKAPI_BASE_URL}/connectionPoints")
    responseJson = response.json()

    tp_id = 0
    for tp in responseJson:
        if (tp["platform"] == "SLL" and tp["environment"] == envir):
            tp_id = tp["id"]

    return tp_id

##################################################################################################


def get_contracts_ids():
    """Get the serviceContractIds for the three request contracts"""

    contract_namespaces = ["urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
                           "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
                           "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1"]

    response = requests.get(f"{TAKAPI_BASE_URL}/serviceContracts")
    responseJson = response.json()

    contracts_ids = []

    for contract in responseJson:
        if (contract["namespace"] in contract_namespaces):
            contracts_ids.append(contract["id"])

    return contracts_ids

##################################################################################################


def service_producer_id(producer):

    response = requests.get(
        f"{TAKAPI_BASE_URL}/serviceServiceProducers?connectionPointId=7&serviceContractId={contract_ids[0]}&include=logicalAddress%2CphysicalAddress")
    responseJson = response.json()

    for route in responseJson:
        print(route)

    return service_component_id

##################################################################################################


def dump_service_producers():
    """Will dump the routes to a file as a backup"""

    contract_ids = get_contracts_ids()

    response = requests.get(f"{TAKAPI_BASE_URL}/serviceProductions")
    responseJson = response.json()

    for route in responseJson:
        print(route)

##################################################################################################


def create_ntjp_files(envir: str) -> None:
    """Will create json files for NTJP"""

    # Prepare placeholders for update file
    logiskaAdresser = []

    update = get_header("NTJP", envir)
    update_include = {}
    update_vagval_include = []

    # Calculate base information
    contracts_ids = get_contracts_ids()
    tp_id = get_connection_point_id(envir)

    # Producers
    cosmic_hsaid = PRODUCER_HSA_ID[f"COSMIC-{envir}"]
    cosmic_description = PRODUCER_DESCRIPTION[f"COSMIC-{envir}"]

    takecare_hsaid = PRODUCER_HSA_ID[f"TAKECARE-{envir}"]
    takecare_description = PRODUCER_DESCRIPTION[f"TAKECARE-{envir}"]

    rtp_hsaid = PRODUCER_HSA_ID[f"RTP-{envir}"]
    rtp_description = PRODUCER_DESCRIPTION[f"RTP-{envir}"]
    
    ntjp_hsaid = PRODUCER_HSA_ID[f"NTJP-{envir}"]
    ntjp_description = PRODUCER_DESCRIPTION[f"NTJP-{envir}"]

    if (envir == "QA"):
        rtp_producer_hsa = PRODUCER_HSA_ID["RTP-QA"]
        cosmic_producer_hsa = PRODUCER_HSA_ID["COSMIC-QA"]
    elif(envir == "PROD"):
        rtp_producer_hsa = PRODUCER_HSA_ID["RTP-PROD"]
        cosmic_producer_hsa = PRODUCER_HSA_ID["COSMIC-PROD"]


    # Get the ServiceProductions for the NTJP QA or PROD TAK
    service_productions = requests.get(
        f"{TAKAPI_BASE_URL}/serviceProductions?connectionPointId={tp_id}&include=serviceContract%2ClogicalAddress%2CphysicalAddress,serviceProducer")

    production_json = service_productions.json()

    # Loop thorugh all routes in the RTP TAK. Create vagval in NTJP based on the RTP production information.
    #       A. productions pointing to COSMIC should be "copied" to NTJP
    #       B. productions pointing to TakeCare should be added to NTJP pointing to RTP
    for production in production_json:

        # Find production in the request domain pointing to Capio COSMIC
        if (production["serviceContract"]["id"] in contracts_ids and production["serviceProducer"]["hsaId"] == cosmic_hsaid):
            # print(route)

            namespace = production["serviceContract"]["namespace"]

            logiskAdress = {
                "hsaId": production["logicalAddress"]["logicalAddress"],
                "beskrivning": production["logicalAddress"]["description"]
            }
            
            cosmic_producer_url = get_producer_url("COSMIC", envir, namespace)

            # Add a include of this logical address
            if (logiskAdress not in logiskaAdresser):
                logiskaAdresser.append(logiskAdress)


            # Add the include of this vagval. The vagval should point to the cosmic producer.
            update_vagval_include.append({
                "tjanstekomponent": cosmic_producer_hsa,
                "adress": cosmic_producer_url,
                "logiskAdress": production["logicalAddress"]["logicalAddress"],
                "tjanstekontrakt": namespace,
                "rivtaprofil": "RIVTABP21"
            })

        # Find production in the request domain pointing to TakeCare
        elif (production["serviceContract"]["id"] in contracts_ids and production["serviceProducer"]["hsaId"] == takecare_hsaid):
            # print(route)

            namespace = production["serviceContract"]["namespace"]

            logiskAdress = {
                "hsaId": production["logicalAddress"]["logicalAddress"],
                "beskrivning": production["logicalAddress"]["description"]
            }
            
            producer_url = get_producer_url("RTP", envir, namespace)

            # Add a include of this logical address
            if (logiskAdress not in logiskaAdresser):
                logiskaAdresser.append(logiskAdress)


            # Add the include of this vagval. The vagval should point to the cosmic producer.
            update_vagval_include.append({
                "tjanstekomponent": rtp_producer_hsa,
                "adress": producer_url,
                "logiskAdress": production["logicalAddress"]["logicalAddress"],
                "tjanstekontrakt": namespace,
                "rivtaprofil": "RIVTABP21"
            })

    # Finally, create the files
    update_include["tjanstekomponenter"] = [
        {
            "hsaId": cosmic_hsaid,
            "beskrivning": cosmic_description
        },
        {
            "hsaId": rtp_hsaid,
            "beskrivning": rtp_description
        }

    ]  

    update_include["tjanstekontrakt"] = get_json_contracts()
    update_include["logiskadresser"] = logiskaAdresser
    update_include["vagval"] = update_vagval_include

    update = get_header("NTJP", envir)
    update["inkludera"] = update_include

    printerr(f"Generating UPDATE file for NTJP-{envir} ")
    print(json.dumps(update, ensure_ascii=False))

        # print(json.dumps(update_include, ensure_ascii=False))
    # print("here is your checkmark: " + u'\u2713');

##################################################################################################



def create_rtp_files(envir: str, phase: str) -> None:
    """Will create json files for RTP"""

    # Prepare placeholders for update and rollback files
    logiskaAdresser = []

    update = get_header("RTP", envir)
    update_include = {}
    update_vagval_include = []

    rollback = get_header("RTP", envir)
    rollback_include = {}
    rollback_vagval_include = []

    # Calculate base information
    contracts_ids = get_contracts_ids()
    tp_id = get_connection_point_id(envir)

    cosmic_hsaid = PRODUCER_HSA_ID[f"COSMIC-{envir}"]
    cosmic_description = PRODUCER_DESCRIPTION[f"COSMIC-{envir}"]

    ntjp_hsaid = PRODUCER_HSA_ID[f"NTJP-{envir}"]
    ntjp_description = PRODUCER_DESCRIPTION[f"NTJP-{envir}"]

    if (envir == "QA"):
        ntjp_producer_hsa = PRODUCER_HSA_ID["NTJP-QA"]
        cosmic_producer_hsa = PRODUCER_HSA_ID["COSMIC-QA"]
    elif(envir == "PROD"):
        ntjp_producer_hsa = PRODUCER_HSA_ID["NTJP-PROD"]
        cosmic_producer_hsa = PRODUCER_HSA_ID["COSMIC-PROD"]


    # Get the ServiceProductions for the RTP QA or PROD TAK
    service_productions = requests.get(
        f"{TAKAPI_BASE_URL}/serviceProductions?connectionPointId={tp_id}&include=serviceContract%2ClogicalAddress%2CphysicalAddress,serviceProducer")

    production_json = service_productions.json()
    #service_productions_unicode = requests.utils.get_unicode_from_response(service_productions)
    #production_json = json.loads(service_productions_unicode)

    # Loop thorugh all routes to COSMIC should change to NTJP
    for production in production_json:

        # Find production in the request domain pointing to Capio COSMIC
        if (production["serviceContract"]["id"] in contracts_ids and production["serviceProducer"]["hsaId"] == cosmic_hsaid):
            # print(route)

            namespace = production["serviceContract"]["namespace"]

            logiskAdress = {
                "hsaId": production["logicalAddress"]["logicalAddress"],
                "beskrivning": production["logicalAddress"]["description"]
            }

            if (logiskAdress not in logiskaAdresser):
                logiskaAdresser.append(logiskAdress)

            ##################################################################
            # Update
            """During update the producer COSMIC should change to NTJP. Different producer and URL"""

            ntjp_producer_url = get_producer_url("NTJP", envir, namespace)

            # The new routes (vagval) should point to NTJP
            update_vagval_include.append({
                "tjanstekomponent": ntjp_producer_hsa,
                "adress": ntjp_producer_url,
                "logiskAdress": production["logicalAddress"]["logicalAddress"],
                "tjanstekontrakt": namespace,
                "rivtaprofil": "RIVTABP21"
            })

            ##################################################################
            # Rollback
            cosmic_producer_url = get_producer_url("COSMIC", envir, namespace)

            # The new routes (vagval) should point to NTJP
            rollback_vagval_include.append({
                "tjanstekomponent": cosmic_producer_hsa,
                "adress": cosmic_producer_url,
                "logiskAdress": production["logicalAddress"]["logicalAddress"],
                "tjanstekontrakt": namespace,
                "rivtaprofil": "RIVTABP21"
            })

    # Finally, create the files
    update_include["tjanstekomponenter"] = [
        {
            "hsaId": cosmic_hsaid,
            "beskrivning": cosmic_description
        },
        {
            "hsaId": ntjp_hsaid,
            "beskrivning": ntjp_description
        }

    ]
    rollback_include["tjanstekomponenter"] = update_include["tjanstekomponenter"]

    update_include["tjanstekontrakt"] = get_json_contracts()
    rollback_include["tjanstekontrakt"] = get_json_contracts()

    update_include["logiskadresser"] = logiskaAdresser
    rollback_include["logiskadresser"] = logiskaAdresser

    update_include["vagval"] = update_vagval_include
    rollback_include["vagval"] = rollback_vagval_include

    if (phase == "UPDATE"):
        update = get_header("RTP", envir)
        update["inkludera"] = update_include

        printerr(f"Generating UPDATE file for RTP-{envir} ")
        print(json.dumps(update, ensure_ascii=False))

    elif (phase == "ROLLBACK"): 
        rollback = get_header("RTP", envir)
        rollback["inkludera"] = rollback_include

        printerr(f"Generating ROLLBACK for RTP-{envir} ")
        print(json.dumps(rollback, ensure_ascii=False))

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

# Environment: prod | qa
# Target: ntjp | rtp
# Phase: update | remove | rollback

ARG_ENVIRONMENT = ["prod", "qa"]
ARG_TARGET = ["ntjp", "rtp"]
ARG_PHASE = ["update", "remove", "rollback"]

parser.add_argument("-e", "--environment", action="store",
                    help="prod | qa", required=True)
parser.add_argument("-t", "--target", action="store",
                    help="ntjp | rtp", required=True)
parser.add_argument("-p", "--phase", action="store",
                    help="update | remove | rollback", required=True)
parser.add_argument("-s", "--sample", action='store_true',
                    help="create sample files")
parser.set_defaults(sample=False)

args = parser.parse_args()

environment = args.environment.lower()
target = args.target.lower()
phase = args.phase.lower()
create_sample = args.sample

if (environment not in ARG_ENVIRONMENT or target not in ARG_TARGET or phase not in ARG_PHASE):
    parser.print_help()
    exit()

##################################################################################################
# Set up global variables

SOURCE_TAK_PLATFORM = "SLL"
SOURCE_TAK_ENVIRONMENT = environment.upper()
TARGET_TP = target.upper()
TARGET_ENVIRONMENT = SOURCE_TAK_ENVIRONMENT
PHASE = phase.upper()

PRODUCER_HSA_ID = {"COSMIC-QA": "SE5565189692-B05",
                   "COSMIC-PROD": "SE5565189692-B03",
                   "TAKECARE-QA": "SE2321000016-AM8S",
                   "TAKECARE-PROD": "SE2321000016-F835",
                   "NTJP-QA": "T-SERVICES-SE165565594230-1023",
                   "NTJP-PROD": "HSASERVICES-106J",
                   "RTP-QA": "SE2321000016-AMCV",
                   "RTP-PROD": "SE2321000016-FH3P"}

PRODUCER_DESCRIPTION = {"COSMIC-QA": "Capio AB -- Cosmic -- St Görans sjukhus",
                        "COSMIC-PROD": "Capio AB -- Cosmic -- Capio St Göran",
                        "TAKECARE-QA": "Region Stockholm -- EDI -- TakeCare",
                        "TAKECARE-PROD": "Region Stockholm -- EDI som tjänsteproducent -- Ny tjänsteproducent fr o m 2021-10-12, har ersatt tidigare producent ""...4HR3"".",
                        "NTJP-QA": "Inera AB -- Tjänsteplattform -- Nationella tjänster",
                        "NTJP-PROD": "Inera AB -- Tjänsteplattform -- Nationella tjänster",
                        "RTP-QA": "Region Stockholm -- Tjänsteplattform som tjänsteproducent -- Tjänsteproducent fr o m 2021-09-22, ersätter ""...-A2G4"" som producent!",
                        "RTP-PROD": "Region Stockholm -- Tjänsteplattform som tjänsteproducent -- Tjänsteproducent fr o m 2021-09-22, ersätter ""...-7P35"" som producent!"}

PRODUCER_URL = {"COSMIC-QA": [
    "https://testcosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequest",
    "https://testcosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequestConfirmation",
    "https://testcosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequestOutcome"
],
    "COSMIC-PROD": [
    "https://cosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequest",
    "https://cosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequestConfirmation",
    "https://cosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequestOutcome"
],
    "TAKECARE-QA": [
    "https://test-api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
    "https://test-api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
    "https://test-api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21"
],
    "TAKECARE-PROD": [
    "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
    "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
    "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
],
    "NTJP-QA": [
    "https://qa.esb.ntjp.se/vp",
    "https://qa.esb.ntjp.se/vp",
    "https://qa.esb.ntjp.se/vp"
],
    "NTJP-PROD": [
    "https://esb.ntjp.se/vp",
    "https://esb.ntjp.se/vp",
    "https://esb.ntjp.se/vp"
],
    "RTP-QA": [
    "https://qa.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
    "https://qa.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestConfirmation/1/rivtabp21",
    "https://qa.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestOutcome/1/rivtabp21"
],
    "RTP-PROD": [
    "https://prod.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
    "https://prod.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestConfirmation/1/rivtabp21",
    "https://prod.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestOutcome/1/rivtabp21"
]
}

TAKAPI_BASE_URL = "http://api.ntjp.se/coop/api/v1"

SERVICE_CONTRACT_NAMESPACE = {
    "ProcessRequest": "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
    "ProcessRequestConfirmation": "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
    "ProcessRequestOutcome": "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1"
}

##################################################################################################
# Main program switch
if (create_sample and (PHASE == "UPDATE" or PHASE == "REMOVE")):
    create_sample_files(TARGET_TP, TARGET_ENVIRONMENT, PHASE)

elif (TARGET_TP == "RTP"):
    create_rtp_files(TARGET_ENVIRONMENT, PHASE)
elif (TARGET_TP == "NTJP"):
    create_ntjp_files(TARGET_ENVIRONMENT)

exit()
