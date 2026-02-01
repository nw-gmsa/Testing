# Examples 

Are based on [North West Genomics Test Patients](https://nw-gmsa.github.io/testing.html#integration-testing)
These patients are also registered on [NHS England Personal Demographics Service - FHIR API - Integration Environment](https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir)

# Sending HL7 v2 Message

Note files must use CR or CRLF (not unix/mac LF)

## Mac

### Transform to FHIR

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_PDF.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_DLIMS.txt" http://192.168.1.20:9981/transformToFHIR

Round Trip Pairs

curl --request POST --data-binary "@Input/V2/O21/OML_O21_RPY.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RPY.txt" http://192.168.1.20:9981/transformToFHIR

curl --request POST --data-binary "@Input/V2/O21/OML_O21_R0A.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9981/transformToFHIR

MFT Multiple Tests example

curl --request POST --data-binary "@Specifications/ManchesterFoundationTrust/ORM_O01-MultipleTests.txt" http://192.168.1.20:9981/transformToFHIR

### Send to HL7v2 Receiver

Round Trip

curl --request POST --data-binary "@Input/V2/O21/OML_O21_RPY.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RPY.txt" http://192.168.1.20:9980

curl --request POST --data-binary "@Input/V2/O21/OML_O21_R0A.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9980

Note file must use \r mac line endings.

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_R0A.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RBS.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_REP.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RPY.txt" http://192.168.1.20:9980

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_PDF.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_DLIMS.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_REP.txt" http://192.168.1.20:9980

Other English Region

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RX1.txt" http://192.168.1.20:9980
curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_RR8.txt" http://192.168.1.20:9980

CHI Number example

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_SG9.txt" http://192.168.1.20:9980

Health and Care Number Example

curl --request POST --data-binary "@Input/V2/R01/ORU_R01_R125.1_ZT001.txt" http://192.168.1.20:9980

## Windows

`Invoke-RestMethod -Method POST -Uri http://localhost:9980 -InFile "Specifications/ManchesterFoundationTrust/OML_O21_PDF.txt"`
`Invoke-RestMethod -Method POST -Uri http://localhost:9980 -InFile "Specifications/ManchesterFoundationTrust/ORU_R01_PDF.txt"`
`Invoke-RestMethod -Method POST -Uri http://localhost:9980 -InFile "Examples/ORU_R01_PDF.txt"`
`Invoke-RestMethod -Method POST -Uri http://localhost:9981/transformToFHIR -InFile "Examples/ORU_R01_PDF.txt"`
