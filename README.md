Virual Environment 3.12 (scispacy compatible)

Additional commands to run:
- python -m spacy download en_core_web_sm
- pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz

# Examples 

Are based on [North West Genomics Test Patients](https://nw-gmsa.github.io/testing.html#integration-testing)
These patients are also registered on [NHS England Personal Demographics Service - FHIR API - Integration Environment](https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir)

# Sending HL7 v2 Message

Note files must use CR or CRLF (not unix/mac LF)

## Unstructured Report and Structured Order Examples

### Transform to FHIR

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_PDF.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_DLIMS.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/O21/ORM_O01_R0A.txt" http://192.168.1.20:9981/transformToFHIR


#### Round Trip Pairs

curl --request POST --data-binary "@Input/V2/O21/OML_O21_RPY.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RPY.txt" http://192.168.1.20:9981/transformToFHIR

curl --request POST --data-binary "@Input/V2/O21/OML_O21_R0A.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Output/FHIR/R01/ORU_R01_R125.1_R0A.txt.json" http://192.168.1.20:9981/transformToV2

#### MFT Multiple Tests example

curl --request POST --data-binary "@Specifications/ManchesterFoundationTrust/ORM_O01-MultipleTests.txt" http://192.168.1.20:9981/transformToFHIR

#### Shire and DHCW ORU_R01 

To FHIR 

curl --request POST --data-binary "@Input/V2/R01/SHIRE_ORU_R01_RM3.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/WALES_ORU_R01_TX.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/WALES_ORU_R01_FULL.txt" http://192.168.1.20:9981/transformToFHIR

From FHIR 

curl --request POST --data-binary "@Output/FHIR/R01/WALES_ORU_R01_TX.txt.json" http://192.168.1.20:9981/transformToV2
curl --request POST --data-binary "@Output/FHIR/R01/WALES_ORU_R01_FULL.txt.json" http://192.168.1.20:9981/transformToV2

### Send to HL7v2 Receiver

Note file must use \r mac line endings

#### Round Trip

curl --request POST --data-binary "@Input/V2/O21/OML_O21_RPY.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RPY.txt" http://192.168.1.20:9980

curl --request POST --data-binary "@Input/V2/O21/OML_O21_R0A.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9980

#### Reports

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RBS.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_REP.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RPY.txt" http://192.168.1.20:9980

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_PDF.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_DLIMS.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_REP.txt" http://192.168.1.20:9980

#### Other English Region Reports

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RX1.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RR8.txt" http://192.168.1.20:9980

#### Scotland - CHI Number example

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_SG9.txt" http://192.168.1.20:9980

#### Northern Ireland - Health and Care Number Example

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_ZT001.txt" http://192.168.1.20:9980

### Windows

`Invoke-RestMethod -Method POST -Uri http://localhost:9980 -InFile "Specifications/ManchesterFoundationTrust/OML_O21_PDF.txt"`
`Invoke-RestMethod -Method POST -Uri http://localhost:9980 -InFile "Specifications/ManchesterFoundationTrust/ORU_R01_PDF.txt"`
`Invoke-RestMethod -Method POST -Uri http://localhost:9980 -InFile "Examples/ORU_R01_PDF.txt"`
`Invoke-RestMethod -Method POST -Uri http://localhost:9981/transformToFHIR -InFile "Examples/ORU_R01_PDF.txt"`

## Structured Report Examples

Examples are from [HL7 Lab Results Interface (LRI), Release 1 from May 2017](https://confluence.hl7.org/download/attachments/25559919/2018%2004%2003%20-%20V2%20LRI%20-%20Ch.%205%20CG%20and%20Code%20System%20Tables.pdf?api=v2)

### Transform to FHIR

curl --request POST --data-binary "@Input/V2/R01/LRI_GeneVariant-1.txt" http://192.168.1.20:9981/transformToFHIR

### Send to HL7v2 Receiver

curl --request POST --data-binary "@Input/V2/R01/LRI_GeneVariant-1.txt" http://192.168.1.20:9980


## WeasyPrint Issues

> export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH
