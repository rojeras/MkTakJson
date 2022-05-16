from datetime import datetime
import json
import sys

# A couple of classes to manage and generate the BS-json files

def printerr(text):
    print(text, file=sys.stderr)

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
                    component: object,
                    address: object,
                    logicalAddress: object,
                    namespace: object,
                    rivtaProfile: object = "RIVTABP21") -> object:
        """

        :rtype: object
        """
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

    # """

