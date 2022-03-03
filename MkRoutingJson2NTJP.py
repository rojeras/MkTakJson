from email import parser
from random import sample
from datetime import datetime
import requests
import argparse
import json

##################################################################################################
def get_order_header(target_tp, target_envir):

    plattform = f'{target_tp}-{target_envir}'

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0100")

    return {
        "plattform" : plattform,
        "formatVersion": "1.0",
        "version": "1",
        "bestallningsTidpunkt": now,
        "utforare": "SLL RTP",
        "genomforandeTidpunkt": now,
    }


##################################################################################################
def connectionPointId():
    """Get the connectionPointId of the RTP-{SOURCE_TAK_ENVIRONMENT}"""
    response = requests.get(f"{TAKAPI_BASE_URL}/connectionPoints")
    responseJson = response.json()

    tp_id = 0
    for tp in responseJson:
        if (tp["platform"] == SOURCE_TAK_PLATFORM and tp["environment"] == SOURCE_TAK_ENVIRONMENT):
            tp_id = tp["id"]

    return tp_id

##################################################################################################
def contracts_ids():
    """Get the serviceContractIds for the three request contracts"""

    contract_namespaces = ["urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
            "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
            "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1"]

    response = requests.get(f"{TAKAPI_BASE_URL}/serviceContracts?connectionPointId={connectionPointId()}")
    responseJson = response.json()

    contracts_ids = []

    for contract in responseJson:
        if (contract["namespace"] in contract_namespaces):
            contracts_ids.append(contract["id"])
    
    return contracts_ids

##################################################################################################
def service_producer_id(producer):

    response = requests.get(f"{TAKAPI_BASE_URL}/serviceServiceProducers?connectionPointId=7&serviceContractId={contract_ids[0]}&include=logicalAddress%2CphysicalAddress")
    responseJson = response.json()

    for route in responseJson:
        print(route)


    return service_component_id

##################################################################################################
def dump_service_producers():
    """Will dump the routes to a file as a backup"""

    contract_ids = contracts_ids()

    response = requests.get(f"{TAKAPI_BASE_URL}/serviceProductions")
    responseJson = response.json()

    for route in responseJson:
        print(route)

##################################################################################################
def create_sample_files(target_tp, target_envir):
    body = get_order_header(target_tp, target_envir)

    include = {}
    include["tjanstekontrakt"] = get_json_contracts()
    include["tjanstekomponenter"] = get_sample_service_components()
    include["logiskadresser"] = get_sample_logical_addresses()
    include["vagval"] = get_sample_routes()

    body["inkludera"] = include

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
def rtp_update():
    """Will create update statements for RTP"""
    
    response = requests.get(f"{TAKAPI_BASE_URL}/serviceProductions?connectionPointId=7&serviceContractId=117&include=logicalAddress%2CphysicalAddress")
    responseJson = response.json()

    for route in responseJson:
        print(route)

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

parser.add_argument("-e", "--environment", action="store", help="prod | qa", required=True)
parser.add_argument("-t", "--target", action="store", help="ntjp | rtp", required=True)
parser.add_argument("-p", "--phase", action="store", help="update | remove | rollback", required=True)
parser.add_argument("-s", "--sample", action='store_true', help="create sample files")
parser.set_defaults(sample=False)

args = parser.parse_args()

environment = args.environment.lower()
target = args.target.lower()
phase = args.phase.lower()
create_sample = args.sample 

print(create_sample)

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

PRODUCER_HSA_ID = { "COSMIC-QA" : "SE5565189692-B05", 
                    "COSMIC-PROD" : "SE5565189692-B03",
                    "TAKECARE-QA" : "SE2321000016-AM8S",
                    "TAKECARE-PROD" : "SE2321000016-F835",
                    "NTJP-QA" : "T-SERVICES-SE165565594230-1023",
                    "NTJP-PROD" : "HSASERVICES-106J",
                    "RTP-QA" : "SE2321000016-AMCV",
                    "RTP-PROD" : "SE2321000016-FH3P"} 

PRODUCER_URL = {    "COSMIC-QA" : [
                        "https://testcosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequest",
                        "https://testcosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequestConfirmation",
                        "https://testcosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequestOutcome"
                        ], 
                    "COSMIC-PROD" : [
                        "https://cosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequest",
                        "https://cosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequestConfirmation",
                        "https://cosmic.capiostgoran.sjunet.org/EReferralWebservice/ProcessRequestOutcome"
                    ],
                    "TAKECARE-QA" : [
                        "https://test-api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
                        "https://test-api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
                        "https://test-api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21"
                        ],
                    "TAKECARE-PROD" : [
                        "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
                        "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
                        "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
                        ],
                    "NTJP-QA" : [
                        "https://qa.esb.ntjp.se/vp", 
                        "https://qa.esb.ntjp.se/vp", 
                        "https://qa.esb.ntjp.se/vp"
                        ],
                    "NTJP-PROD" : [
                        "https://esb.ntjp.se/vp", 
                        "https://esb.ntjp.se/vp", 
                        "https://esb.ntjp.se/vp"
                        ],
                    "RTP-QA" : [
                        "https://qa.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
                        "https://qa.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestConfirmation/1/rivtabp21",
                        "https://qa.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestOutcome/1/rivtabp21"
                        ],
                    "RTP-PROD" : [
                        "https://prod.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21", 
                        "https://prod.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestConfirmation/1/rivtabp21",
                        "https://prod.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestOutcome/1/rivtabp21"
                        ]
                        } 

TAKAPI_BASE_URL = "http://api.ntjp.se/coop/api/v1"


##################################################################################################
# Main program switch
if (create_sample):
    create_sample_files(TARGET_TP, TARGET_ENVIRONMENT)


elif (TARGET_TP == "RTP"):
    if (PHASE == "UPDATE"): 
        rtp_update()
    else:
        print("Not yet implemented") 
else:
    print("Not yet implemented") 

exit()



