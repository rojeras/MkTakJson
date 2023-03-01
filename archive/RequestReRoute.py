import sys
import argparse
import json
from BsJson import BsJson, BsJsonSection
##################################################################################################
"""
This script was used in the spring 2022 to reroute requests (remisser) to and from Capio Cosmic
to go through NTJP. Based on the old TAK config in RTP it generated TAK JSON files for the new 
configuration in both NTJP and RTP. It also generated rollback files for RTP (not needed for
NTJP). 
Input to the script was a dump from the TAK-api. The dump is obtained by dumping the output from
takapiProductions.sh to file and provide the filename as an argument to this program.

Since the change of configuration was a one time effort this script is not expected to be used 
in the future. But, there might be a need for something similar, where this code can serve as 
inspiration.

LEO 2023-01-24
"""

##################################################################################################
def printerr(text):
    print(text, file=sys.stderr)


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


def create_json_file(target: str, envir: str, phase: str) -> None:
    """Will create json file"""

    current_mappings = MAPPINGS[target]

    current_mappings_hsaids = []
    for key in current_mappings.keys():
        current_mappings_hsaids.append(PRODUCER_HSA_ID[f"{key}-{envir}"])

    include_section = BsJsonSection()

    for contract in SERVICE_CONTRACTS:
        include_section.add_contract(contract["namnrymd"], contract["beskrivning"])

    production_json = json.load(SERVICE_PRODUCTION_FILE)

    # Loop through all routes to COSMIC should change to NTJP
    for production in production_json:

        # Remove all productions not referring to the request contracts
        if (
                production["serviceContract"]["namespace"].startswith(
                    "urn:riv:clinicalprocess:activity:request:ProcessRequest") and
                production["connectionPoint"]["platform"] == "SLL" and
                production["connectionPoint"]["environment"] == envir
        ):

            production_system = ""
            producer_system = ""
            found = False
            # Verify that this production is in the mappings list of systems which should be mapped
            for key, value in current_mappings.items():
                if (PRODUCER_HSA_ID[f"{key}-{envir}"] == production["serviceProducer"]["hsaId"]):
                    production_system = key
                    producer_system = value
                    found = True

            # Iterate if this is not a production that should be mapped
            if (not found):
                continue

            namespace = production["serviceContract"]["namespace"]

            include_section.add_logicalAddress(
                production["logicalAddress"]["logicalAddress"],
                production["logicalAddress"]["description"]
            )

            if phase == "UPDATE":

                include_section.add_component(
                    PRODUCER_HSA_ID[f"{producer_system}-{envir}"],
                    PRODUCER_DESCRIPTION[f"{producer_system}-{envir}"]
                )

                include_section.add_routing(
                    PRODUCER_HSA_ID[f"{producer_system}-{envir}"],
                    get_producer_url(producer_system, envir, namespace),
                    production["logicalAddress"]["logicalAddress"],
                    namespace
                )

            elif phase == "ROLLBACK":
                include_section.add_component(
                    PRODUCER_HSA_ID[f"{production_system}-{envir}"],
                    PRODUCER_DESCRIPTION[f"{production_system}-{envir}"]
                )

                include_section.add_routing(
                    PRODUCER_HSA_ID[f"{production_system}-{envir}"],
                    get_producer_url(production_system, envir, namespace),
                    production["logicalAddress"]["logicalAddress"],
                    namespace
                )

            else:
                printerr(f"phase must be UPDATE or ROLLBACK, not {phase}!")
                exit(1)

    # Print out the JSON data
    content = BsJson(TARGET_TP_ENVIR)
    content.add_section("include", include_section)
    content.print_json()


################################################################################################
#                                 Main Program
################################################################################################
# Parse arguments
parser = argparse.ArgumentParser()

# Environment: prod | qa
# Target: ntjp | rtp
# Phase: update | remove | rollback

ARG_ENVIRONMENT = ["prod", "qa"]
ARG_TARGET = ["ntjp", "rtp"]
ARG_PHASE = ["update", "rollback"]

parser.add_argument("-t", "--target", action="store",
                    help="ntjp | rtp", required=True)
parser.add_argument("-e", "--environment", action="store",
                    help="prod | qa", required=True)
parser.add_argument("-p", "--phase", action="store",
                    help="update | rollback", required=True)
parser.add_argument("-s", "--sample", action='store_true',
                    help="create sample files")
parser.add_argument("filename", nargs=1, type=argparse.FileType('r'))
parser.set_defaults(sample=False)

args = parser.parse_args()

environment = args.environment.lower()
target = args.target.lower()
phase = args.phase.lower()
create_sample = args.sample
service_productions_file = args.filename[0]

if (environment not in ARG_ENVIRONMENT or target not in ARG_TARGET or phase not in ARG_PHASE):
    parser.print_help()
    exit()

##################################################################################################
# Set up global variables


MAPPINGS = {
    "RTP": {  # In RTP
        "COSMIC": "NTJP"  # productions refering to COSMIC should get vagval to NTJP
    },
    "NTJP": {  # In NTJP
        "TAKECARE": "RTP",  # production refering to TakeCare should get vagval to RTP
        "COSMIC": "COSMIC"  # productions refering to COSMIC should get vagval to COSMIC
    }
}

SOURCE_TAK_PLATFORM = "SLL"
SOURCE_TAK_ENVIRONMENT = environment.upper()
TARGET_TP = target.upper()
TARGET_TP_ENVIR = f"{TARGET_TP}-{environment.upper()}"
TARGET_ENVIRONMENT = SOURCE_TAK_ENVIRONMENT
PHASE = phase.upper()
SERVICE_PRODUCTION_FILE = service_productions_file

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

PRODUCER_URL = {
    "COSMIC-QA": [
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
        "https://rtp.qa.internet.regionstockholm.se/vp/clinicalprocess/activity/request/ProcessRequest/1",
        "https://rtp.qa.internet.regionstockholm.se/vp/clinicalprocess/activity/request/ProcessRequestConfirmation/1",
        "https://rtp.qa.internet.regionstockholm.se/vp/clinicalprocess/activity/request/ProcessRequestOutcome/1"
        # "https://qa.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
        # "https://qa.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestConfirmation/1/rivtabp21",
        # "https://qa.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestOutcome/1/rivtabp21"
    ],
    "RTP-PROD": [
        "https://rtp.prod.internet.regionstockholm.se/vp/clinicalprocess/activity/request/ProcessRequest/1",
        "https://rtp.prod.internet.regionstockholm.se/vp/clinicalprocess/activity/request/ProcessRequestConfirmation/1",
        "https://rtp.prod.internet.regionstockholm.se/vp/clinicalprocess/activity/request/ProcessRequestOutcome/1"
        # "https://prod.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21",
        # "https://prod.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestConfirmation/1/rivtabp21",
        # "https://prod.esb.rtp.sll.se:443/vp/clinicalprocess/activity/request/ProcessRequestOutcome/1/rivtabp21"
    ]
}

TAKAPI_BASE_URL = "http://api.ntjp.se/coop/api/v1"

SERVICE_CONTRACT_NAMESPACE = {
    "ProcessRequest": "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
    "ProcessRequestConfirmation": "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
    "ProcessRequestOutcome": "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1"
}

SERVICE_CONTRACTS = [
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
    },
]
##################################################################################################
# Main program switch
if (TARGET_TP == "NTJP" and PHASE == "ROLLBACK"):
    printerr("rollback is not implemented, nor needed, for NTJP target")
else:
    create_json_file(TARGET_TP, TARGET_ENVIRONMENT, PHASE)

exit()
