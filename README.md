# Allmänt om detta repo
## Funktion
Detta repo innehåller script som skapar BS JSON-fil med TAK-nings-beställningar. Scripten använder den gemensamma modulen
BsJson.py som innehåller klasser för att konstruera JSON enligt Beställningsstödets standard.

## Krav för att kunna använda

* Python3 av senare modell
* git
* Lämplig editor eller IDE

## Installation Linux
1. Klona detta repo
2. Sätt upp pythonmiljön. Det är ofta en god idé att använda en virtuell miljö i Linux:

   ```
   python3 -m venv venv
   source venv/bin/activate  
   python3 -m pip install requests # Enbart för RequestRoutes
   ```

## Installation Windows
1. Klona detta repo
2. Sätt upp pythonmiljön. 

   ``` 
   python3 -m pip install requests # Enbart för RequestRoutes
   ```

# Scriptet RequestRoutes.py
Det förutsätts användas för E-remisskontrakten för att skapa vägval i NTJP-PROD eller RTP-PROD. Flaggan -t/--target används för att ange tjänsteplattform. 

Indata är en semikolon-avgränsad CSV-fil enligt:

* Kolumn 1: Logisk adress
* Kolumn 2: Namn på enhet

Se exempel i SampleCsv.csv

Övrig information för att skapa JSON-beställningarna är hårdkodade i scriptet.

Flaggan "-r" instruerar scriptet att i första hand använda de befintliga enhetsnamn som finns i (någon) TAK - om enheten är TAK-ad (för något tjänstekontrakt) sedan tidigare. Dessa erhålles genom att scriptet hämtar logiska adresser från TAK-api.  

OBS. Modulen BsJson.py är ett bibliotek som delas mellan bs-json och analyze-tak (identiska filer används).


## Användning
```
venv) ➜  MkTakJson git:(master) ✗ ./RequestRoutes.py -h           
usage: RequestRoutes.py [-h] [-r] -t TARGET filename

positional arguments:
  filename              name of CSV file

options:
  -h, --help            show this help message and exit
  -r, --replace         replace logical address descriptions from TAK-api
  -t TARGET, --target TARGET
                        target must be one of NTJP-PROD or SLL-PROD

```

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

# Scriptet WebCertRoutes.py
Det används för masstakning för Webcert. 

Indata är en semikolon-avgränsad CSV-fil enligt:

* Kolumn 1: Logisk adress
* Kolumn 2: Namn på enhet

Se exempel i BS-14620.csv

Övrig information för att skapa JSON-beställningarna är hårdkodade i scriptet.

OBS. Modulen BsJson.py är ett bibliotek som delas mellan bs-json och analyze-tak (identiska filer används).

## Användning
```
(venv) ➜  MkTakJson git:(master) ✗ ./WebCertRoutes.py -h
usage: WebCertRoutes.py [-h] filename

positional arguments:
  filename    name of CSV file

options:
  -h, --help  show this help message and exit

```

## Exempel på utdata
```
{
    "plattform": "NTJP-PROD",
    "formatVersion": "1.0",
    "version": "1",
    "bestallningsTidpunkt": "2023-03-01T19:55:50+0100",
    "utforare": "Inera ICC",
    "genomforandeTidpunkt": "2023-03-01T19:55:50+0100",
    "inkludera": {
        "tjanstekomponenter": [
            {
                "hsaId": "SE5565594230-B8N",
                "beskrivning": "Inera AB -- Intygstjänster -- Webcert"
            },
            {
                "hsaId": "SE5565594230-B31",
                "beskrivning": "Inera AB -- Intygstjänster -- Intygstjänsten och Mina Intyg"
            }
        ],
        "tjanstekontrakt": [
            {
                "namnrymd": "urn:riv:clinicalprocess:healthcond:certificate:SendMessageToCareResponder:2",
                "majorVersion": 2,
                "beskrivning": "SendMessageToCare"
            }
        ],
        "logiskadresser": [
            {
                "hsaId": "SE165565594230-WEBCERT02001",
                "beskrivning": "Inera WebCert - Privatläkare 2001"
            }
        ],
        "anropsbehorigheter": [
            {
                "tjanstekonsument": "SE5565594230-B31",
                "logiskAdress": "SE165565594230-WEBCERT02001",
                "tjanstekontrakt": "urn:riv:clinicalprocess:healthcond:certificate:SendMessageToCareResponder:2"
            }
        ],
        "vagval": [
            {
                "tjanstekomponent": "SE5565594230-B8N",
                "logiskAdress": "SE165565594230-WEBCERT02001",
                "tjanstekontrakt": "urn:riv:clinicalprocess:healthcond:certificate:SendMessageToCareResponder:2",
                "rivtaprofil": "RIVTABP21",
                "adress": "https://webcert.ntjp.intygstjanster.se/services/send-message-to-care/v2.0"
            }
        ]
    }
}

```