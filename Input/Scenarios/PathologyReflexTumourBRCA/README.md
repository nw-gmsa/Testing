# End-to-end test: Pathology to Genomics Reflex - Ovarian Cancer Tumour BRCA

Test cases for the NW-GMSA IG scenario [Pathology to Genomics Reflex - Ovarian Cancer Tumour BRCA](https://nw-gmsa.github.io/en/ExampleScenario-PathologyReflexTumourBRCA.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

The steps are run from the original HL7 v2 messages under `V2/<event>/` by `IntegrationTest.py` (group `scenario_PathologyReflexTumourBRCA`), so the FHIR is the RIE's conversion of them. The v2 messages are hand-authored and kept when the scenario is re-exported. The IG's FHIR Messages under `FHIR/<event>/` are for reference.

## Patients

- Selyse BURNLEY (9737383389)

## Test cases

| Step | Stage | Interaction | From → To | HL7 v2 | FHIR (IG) |
|---|---|---|---|---|---|
| 1 | 1. Genomic Reflex Order (LAB-35) | Send Genomic Reflex Order O21 - pathology report only | Order Filler and Requestor - Royal Blackburn Hospital laboratory → Regional Integration Engine | `V2/O21/01-690D0-OML_O21-ReportOnly.txt` | `FHIR/O21/01-GenomicsOrderMessage-PathologyReflex-ReportOnly.json` |
| 2 | 1. Genomic Reflex Order (LAB-35) | Send Genomic Reflex Order O21 - with discrete pathology results | Order Filler and Requestor - Royal Blackburn Hospital laboratory → Regional Integration Engine | `V2/O21/02-690D0-OML_O21.txt` | `FHIR/O21/02-GenomicsOrderMessage-PathologyReflex.json` |
| 3 | 1. Genomic Reflex Order (LAB-35) | Send Genomic Reflex Order O21 | Regional Integration Engine → Order Filler and Subcontractor - North West GLH | - | `FHIR/O21/02-GenomicsOrderMessage-PathologyReflex.json` |
| 4 | 2. Genomic Report (LAB-36) | Send Genomic Report R01 - PDF only | Order Filler and Subcontractor - North West GLH → Regional Integration Engine | `V2/R01/04-699X0-ORU_R01-PDF.txt` | `FHIR/R01/04-GenomicsReportMessage-PathologyReflex.json` |
| 5 | 2. Genomic Report (LAB-36) | Send Genomic Report R01 - enhanced | Order Filler and Subcontractor - North West GLH → Regional Integration Engine | `V2/R01/05-699X0-ORU_R01-Enhanced.txt` | `FHIR/R01/05-GenomicsReportMessage-PathologyReflex-Enhanced.json` |
| 6 | 2. Genomic Report (LAB-36) | Send Genomic Report R01 | Regional Integration Engine → Order Filler and Requestor - Royal Blackburn Hospital laboratory | - | `FHIR/R01/05-GenomicsReportMessage-PathologyReflex-Enhanced.json` |
