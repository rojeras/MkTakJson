# Funktion
Detta script skapar en BS JSON-fil med vägvalsbeställningar. Det förutsätts användas 
för E-remisskontrakten. Indata är en semikolon-avgränsad CSV-fil enligt:
* Kolumn 1: Logisk adress
* Kolumn 2: Namn på enhet

Se exempel i SampleCsv.csv

Övrig information för att skapa JSON-beställningarna är hårdkodade i scriptet.

Flaggan "-r" instruerar scriptet att i första hand använda de enhetsnamn som finns i TAK - om enheten är TAK-ad (för något tjänstekontrakt) sedan tidigare. 

OBS. Modulen BsJson.py är ett bibliotek som delas mellan bs-json och analyze-tak (identiska filer används).

## Exempel på utdata
```
{
    "plattform": "SLL-PROD",
    "formatVersion": "1.0",
    "version": "1",
    "bestallningsTidpunkt": "2023-01-24T09:05:53+0100",
    "utforare": "Region Stockholm - Forvaltningsobjekt Informationsinfrastruktur",
    "genomforandeTidpunkt": "2023-01-24T09:05:53+0100",
    "inkludera": {
        "tjanstekomponenter": [],
        "tjanstekontrakt": [
            {
                "namnrymd": "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
                "majorVersion": 1,
                "beskrivning": "Submission of a request to a healtcare facility"
            },
            {
                "namnrymd": "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
                "majorVersion": 1,
                "beskrivning": "Submission of a request to a healtcare facility"
            },
            {
                "namnrymd": "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1",
                "majorVersion": 1,
                "beskrivning": "Submission of a request to a healtcare facility"
            }
        ],
        "logiskadresser": [
            {
                "hsaId": "SE2321000016-G08F",
                "beskrivning": "ABC Barnmottagning"
            }
        ],
        "anropsbehorigheter": [],
        "vagval": [
            {
                "tjanstekomponent": "SE2321000016-F835",
                "logiskAdress": "SE2321000016-G08F",
                "tjanstekontrakt": "urn:riv:clinicalprocess:activity:request:ProcessRequestResponder:1",
                "rivtaprofil": "RIVTABP21",
                "adress": "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21"
            },
            {
                "tjanstekomponent": "SE2321000016-F835",
                "logiskAdress": "SE2321000016-G08F",
                "tjanstekontrakt": "urn:riv:clinicalprocess:activity:request:ProcessRequestConfirmationResponder:1",
                "rivtaprofil": "RIVTABP21",
                "adress": "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21"
            },
            {
                "tjanstekomponent": "SE2321000016-F835",
                "logiskAdress": "SE2321000016-G08F",
                "tjanstekontrakt": "urn:riv:clinicalprocess:activity:request:ProcessRequestOutcomeResponder:1",
                "rivtaprofil": "RIVTABP21",
                "adress": "https://api.integration.regionstockholm.se/rivta/clinicalprocess/activity/request/ProcessRequest/1/rivtabp21"
            }
        ]
    }
}
```

# Installation
1. Klona detta repo
2. Sätt upp pythonmiljön. Det är ofta en god idé att använda en virtuell miljö:
    ```
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install requests
   ```
3. Scriptet behöver tillgång till en exekverande mysql/mariadb TAK-databas. En användare med enbart läsrättigheter rekommenderas starkt! 
4. Exekvera `MkRoutingFromCsv.py`. Information om nödvändiga flaggor skrivs ut.
 
# Användning
```
bs-json git:(master) ✗ python3 MkRoutingFromCsv.py -h
usage: MkRoutingFromCsv.py [-h] [-r] filename

positional arguments:
  filename       name of CSV file

options:
  -h, --help     show this help message and exit
  -r, --replace  replace logical address descriptions from TAK-api
```