# End-to-end test: Pathology to Genomics Reflex - Ovarian Cancer Tumour BRCA

Test cases for the NW-GMSA IG scenario [Pathology to Genomics Reflex - Ovarian Cancer Tumour BRCA](https://nw-gmsa.github.io/en/ExampleScenario-PathologyReflexTumourBRCA.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_PathologyReflexTumourBRCA`); FHIR Documents and other resources are for reference.

## Patients

- Selyse BURNLEY (9737383389)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Genomic Reflex Order (LAB-35) | Send Genomic Reflex Order O21 - pathology report only | Order Filler and Requestor - Royal Blackburn Hospital laboratory → Regional Integration Engine | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-PathologyReflex-ReportOnly.json` |
| 2 | 1. Genomic Reflex Order (LAB-35) | Send Genomic Reflex Order O21 - with discrete pathology results | Order Filler and Requestor - Royal Blackburn Hospital laboratory → Regional Integration Engine | FHIR Message O21 | `FHIR/O21/02-GenomicsOrderMessage-PathologyReflex.json` |
| 3 | 1. Genomic Reflex Order (LAB-35) | Send Genomic Reflex Order O21 | Regional Integration Engine → Order Filler and Subcontractor - North West GLH | FHIR Message O21 | `FHIR/O21/02-GenomicsOrderMessage-PathologyReflex.json` |
| 4 | 2. Genomic Report (LAB-36) | Send Genomic Report R01 - PDF only | Order Filler and Subcontractor - North West GLH → Regional Integration Engine | FHIR Message R01 | `FHIR/R01/04-GenomicsReportMessage-PathologyReflex.json` |
| 5 | 2. Genomic Report (LAB-36) | Send Genomic Report R01 - enhanced | Order Filler and Subcontractor - North West GLH → Regional Integration Engine | FHIR Message R01 | `FHIR/R01/05-GenomicsReportMessage-PathologyReflex-Enhanced.json` |
| 6 | 2. Genomic Report (LAB-36) | Send Genomic Report R01 | Regional Integration Engine → Order Filler and Requestor - Royal Blackburn Hospital laboratory | FHIR Message R01 | `FHIR/R01/05-GenomicsReportMessage-PathologyReflex-Enhanced.json` |
