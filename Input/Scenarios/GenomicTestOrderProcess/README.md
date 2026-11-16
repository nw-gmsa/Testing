# End-to-end test: Genomic Test Order Process including order entry and transmission of the order

Test cases for the NW-GMSA IG scenario [Genomic Test Order Process including order entry and transmission of the order](https://nw-gmsa.github.io/en/ExampleScenario-GenomicTestOrderProcess.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_GenomicTestOrderProcess`); FHIR Documents and other resources are for reference.

## Patients

- Octavia CHISLETT (9449305552)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | Complete Genomic Test Order Form | Select Genomic Test Order Form | Order Placer → Form Manager | Not covered | - |
| 2 | Complete Genomic Test Order Form | Pre-populate Order Form | Form Manager → Electronic Patient Record | Not covered | - |
| 4 | Complete Genomic Test Order Form | Complete Genomic Test Order Form. | Order Placer → Electronic Patient Record | Not covered | - |
| 5 | Submit Genomic Test Order Form | Send Laboratory Order ORM_O01 v2 | Electronic Patient Record → Trust Integration Engine | Not covered | - |
| 6 | Submit Genomic Test Order Form | Send Laboratory Order O21 FHIR | Trust Integration Engine → Regional Orchestration Engine | FHIR Message O21 | `FHIR/O21/06-GenomicsOrderMessageAttachment.json` |
| 7 | Submit Genomic Test Order Form | Send Laboratory Order OML_O21 v2 | Regional Orchestration Engine → Order Filler | Not covered | - |
| 9 | Send Order to Regional Genomic CDR | Send Laboratory Order O21 FHIR | Regional Orchestration Engine → Regional Clinical Data Repository | FHIR Message O21 | `FHIR/O21/06-GenomicsOrderMessageAttachment.json` |
| 8 | Collect Sample | Collect sample | Regional Orchestration Engine → Order Filler | Not covered | - |

Other example resources in this scenario:

- `FHIR/Bundle/SDCSearchResults.json`
