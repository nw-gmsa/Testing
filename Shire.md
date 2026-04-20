## Transform to FHIR

Has NW Test Patient

curl --request POST --data-binary "@Input/V2/R01/SHIRE_ORU_R01_RM3.txt" http://192.168.1.20:9981/transformToFHIR

Actual Examples from Shire (MFT)

curl --request POST --data-binary "@Input/V2/R01/Shire-1.txt" http://192.168.1.20:9981/transformToFHIR
curl --request POST --data-binary "@Input/V2/R01/Shire-2.txt" http://192.168.1.20:9981/transformToFHIR

## Send to RIE

curl --request POST --data-binary "@Input/V2/R01/Shire-1.txt" http://192.168.1.20:9980