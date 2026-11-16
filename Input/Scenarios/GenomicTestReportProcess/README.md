# End-to-end test: Genomic Test Report Process

Test cases for the NW-GMSA IG scenario [Genomic Test Report Process](https://nw-gmsa.github.io/en/ExampleScenario-GenomicTestReportProcess.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_GenomicTestReportProcess`); FHIR Documents and other resources are for reference.

## Patients

- Octavia CHISLETT (9449305552)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | Send Report to Order Placer | Send Laboratory Report ORU_R01 v2 | Order Filler → Regional Orchestration Engine | Not covered | - |
| 2 | Send Report to Order Placer | Send Laboratory Report ORU_R01 v2 | Regional Orchestration Engine → Trust Integration Engine | Not covered | - |
| 7 | Send Report to Order Placer | Send Laboratory Report ORU_R01 v2 | Trust Integration Engine → Order Placer/Electronic Patient Record | Not covered | - |
| 4 | Send Report to ICS | Patient Demographics Query | Regional Orchestration Engine → Regional - Genomic Data Platform | Not covered | - |
| 5 | Send Report to ICS | Send Laboratory Report MDM_T02 v2 | Regional Orchestration Engine → ICS - Health Information Exchange | Not covered | - |
| 6 | Send Report to Regional Genomic CDR | Send Laboratory Report R01 FHIR | Regional Orchestration Engine → Regional - Genomic Data Platform | FHIR Message R01 | `FHIR/R01/06-GenomicsReportMessage.json` |

Other example resources in this scenario:

- `FHIR/Bundle/PDQSearchResults.json`
