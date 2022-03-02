import requests

print("Hej hopp")

TARGET_TAK_PLATFORM = "SLL"
TARGET_TAK_ENVIRONMENT = "QA"

BASE_URL = "http://api.ntjp.se/coop/api/v1"

CONTRACTS = ["urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
             "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
             "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1"]

response = requests.get(f"{BASE_URL}/connectionPoints")
responseJson = response.json()

# tp_id = 0

for tp in responseJson:
    if (tp["platform"] == TARGET_TAK_PLATFORM and tp["environment"] == TARGET_TAK_ENVIRONMENT):
        print(tp)
        tp_id = tp["id"]

print(tp_id)


namespace = CONTRACTS[0]
response = requests.get(f"{BASE_URL}/serviceContracts?connectionPointId={tp_id}")
responseJson = response.json()

# tp_id = 0

for contract in responseJson:
    if (contract["namespace"] == namespace):
        print(contract)
        contract_id = contract["id"]

print(tp_id)
print(contract_id)


response = requests.get(f"{BASE_URL}/serviceProductions?connectionPointId=7&serviceContractId=117&include=logicalAddress%2CphysicalAddress")
responseJson = response.json()

# tp_id = 0

for route in responseJson:
        print(route)