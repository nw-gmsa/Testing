Virual Environment 3.12 (scispacy compatible)

Additional commands to run:
- python -m spacy download en_core_web_sm
- pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz

# Examples 

Are based on [North West Genomics Test Patients](https://nw-gmsa.github.io/testing.html#integration-testing)
These patients are also registered on [NHS England Personal Demographics Service - FHIR API - Integration Environment](https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir)

# Unstructured Report and Structured Order Examples

Note files must use CR or CRLF (not unix/mac LF)

## HL7 v2 

### Transform to FHIR

#### O01

curl --request POST --data-binary "@Input/V2/O21/ORM_O01_R0A.txt" http://192.168.1.20:9981/transformToFHIR

curl --request POST --data-binary "@Input/V2/O01/Fetus-LRI-Variant-2-O01.txt" http://192.168.1.20:9981/transformToFHIR

#### R01

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_PDF.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_DLIMS.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/LRI-GeneVariant-2.txt" http://192.168.1.20:9981/transformToFHIR

#### Round Trip Pairs

curl --request POST --data-binary "@Input/V2/O21/OML_O21_RPY.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RPY.txt" http://192.168.1.20:9981/transformToFHIR

curl --request POST --data-binary "@Input/V2/O21/OML_O21_R0A.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Output/FHIR/R01/ORU_R01_R125.1_R0A.txt.json" http://192.168.1.20:9981/transformToV2

#### MFT Tests example

curl --request POST --data-binary "@Input/V2/O01/EPIC-Faulty.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Specifications/ManchesterFoundationTrust/ORM_O01-MultipleTests.txt" http://192.168.1.20:9981/transformToFHIR

#### Shire and DHCW ORU_R01

curl --request POST --data-binary "@Input/V2/R01/igene-hods.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/igene-hods.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/SHIRE_ORU_R01_RM3.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/WALES_ORU_R01_TX.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/WALES_ORU_R01_FULL.txt" http://192.168.1.20:9981/transformToFHIR

#### GS1

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_GS1_RXK.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_GS1_RXK.txt" http://192.168.1.20:9980

#### HL7 LRI/Genomic Report Structured Report Examples

Examples are from [HL7 Lab Results Interface (LRI), Release 1 from May 2017](https://confluence.hl7.org/download/attachments/25559919/2018%2004%2003%20-%20V2%20LRI%20-%20Ch.%205%20CG%20and%20Code%20System%20Tables.pdf?api=v2)


curl --request POST --data-binary "@Input/V2/R01/LRI-GeneVariant-1.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/LRI-GeneVariant-2.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/LRI-GeneVariant-3.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/LRI-GeneVariant-4.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/LRI-ComplexVariant-8.txt" http://192.168.1.20:9981/transformToFHIR

Invalid DOB, so no match 

curl --request POST --data-binary "@Input/V2/R01/LRI-GeneVariant-5.txt" http://192.168.1.20:9980

#### Europe

curl --request POST --data-binary "@Input/V2/R01/R0A-Belgium.txt" http://192.168.1.20:9981/transformToFHIR

### Transform to HL7 v2

curl --request POST --data-binary "@Output/FHIR/R01/WALES_ORU_R01_TX.txt.json" http://192.168.1.20:9981/transformToV2
curl --request POST --data-binary "@Output/FHIR/R01/WALES_ORU_R01_FULL.txt.json" http://192.168.1.20:9981/transformToV2
curl --request POST --data-binary "@Output/FHIR/O21/Fetus-LRI-Variant-2-O01.txt.json" http://192.168.1.20:9981/transformToV2

LRI Example

curl --request POST --data-binary "@Output/FHIR/R01/LRI-GeneVariant-2.txt.json" http://192.168.1.20:9981/transformToV2

## Send to HL7 Receiver

Note file must use \r mac line endings

### Orders 

curl --request POST --data-binary "@Input/V2/O21/OML_O21_RPY.txt" http://192.168.1.20:9980

#### Round Trip

curl --request POST --data-binary "@Input/V2/O21/OML_O21_RPY.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RPY.txt" http://192.168.1.20:9980

curl --request POST --data-binary "@Input/V2/O21/OML_O21_R0A_R125.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9980

### Reports

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RBS.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_REP.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RPY.txt" http://192.168.1.20:9980

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_PDF.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_DLIMS.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_REP.txt" http://192.168.1.20:9980

LRI Example

curl --request POST --data-binary "@Input/V2/R01/LRI-GeneVariant-1.txt" http://192.168.1.20:9980

#### Other UK Regions Reports

England

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RX1.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RR8.txt" http://192.168.1.20:9980

Scotland - CHI Number example

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_SG9.txt" http://192.168.1.20:9980

Northern Ireland - Health and Care Number Example

#### Europe


curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_ZT001.txt" http://192.168.1.20:9980

### Windows

`Invoke-RestMethod -Method POST -Uri http://localhost:9980 -InFile "Specifications/ManchesterFoundationTrust/OML_O21_PDF.txt"`
`Invoke-RestMethod -Method POST -Uri http://localhost:9980 -InFile "Specifications/ManchesterFoundationTrust/ORU_R01_PDF.txt"`
`Invoke-RestMethod -Method POST -Uri http://localhost:9980 -InFile "Examples/ORU_R01_PDF.txt"`
`Invoke-RestMethod -Method POST -Uri http://localhost:9981/transformToFHIR -InFile "Examples/ORU_R01_PDF.txt"`



## WeasyPrint Issues

> export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH
