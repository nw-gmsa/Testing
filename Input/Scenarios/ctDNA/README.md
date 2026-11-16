# End-to-end test: Lung Cancer - Liquid Biopsy (ctDNA)

Test cases for the NW-GMSA IG scenario [Lung Cancer - Liquid Biopsy (ctDNA)](https://nw-gmsa.github.io/en/ExampleScenario-ctDNA.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_ctDNA`); FHIR Documents and other resources are for reference.

## Patients

- Theon SHEFFIELD (9737873858)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order O21 | Order Placer/Electronic Patient Record → Regional Integration Engine | Not covered | - |
| 2 | 1. Laboratory Order (LAB-1) | Send Laboratory Order O21 | Regional Integration Engine → Lab 1 - Order Filler LIMS | Not covered | - |
| 3 | 1. Laboratory Order (LAB-1) | Send copy of Laboratory Order using $process-message | Regional Integration Engine → FHIR Repository | Not covered | - |
| 4 | 2. Work Order (LAB-4) | Send Work Order | Lab 1 - Order Filler LIMS → Lab 2 - Automation Manager LIMS | Not covered | - |
| 5 | 2. Work Order (LAB-4) | Send Work Order | Lab 1 - Order Filler LIMS → Regional Integration Engine | Not covered | - |
| 6 | 2. Work Order (LAB-4) | Store Work Order | Regional Integration Engine → FHIR Repository | Not covered | - |
| 7 | 3. Analytics Processing | Send sequencing data | Lab 2 - Automation Manager LIMS → Analytics Processing | Not covered | - |
| 8 | 3. Analytics Processing | Retrieve Work Order | Analytics Processing → FHIR Repository | Not covered | - |
| 9 | 4. Test Results (LAB-5) | Send Test Results R01 | Lab 2 - Automation Manager LIMS → Regional Integration Engine | Not covered | - |
| 10 | 4. Test Results (LAB-5) | Send Test Results R01 | Regional Integration Engine → Lab 1 - Order Filler LIMS | Not covered | - |
| 11 | 4. Test Results (LAB-5) | Send copy of Test Results using $process-message | Regional Integration Engine → FHIR Repository | Not covered | - |
| 12 | 5. Laboratory Report (LAB-3) | Send Laboratory Report R01 | Lab 1 - Order Filler LIMS → Regional Integration Engine | Not covered | - |
| 13 | 5. Laboratory Report (LAB-3) | Send Laboratory Report R01 | Regional Integration Engine → Order Placer/Electronic Patient Record | Not covered | - |
| 14 | 5. Laboratory Report (LAB-3) | Send copy of Laboratory Report using $process-message | Regional Integration Engine → FHIR Repository | Not covered | - |
| 15 | 5. Laboratory Report (LAB-3) | Send Laboratory Report document | Regional Integration Engine → Regional Shared Care Record | FHIR Message T02 | `FHIR/T02/15-DocumentMessage-ctDNA.json` |
| 16 | 6. FHIR Document to Central Registry | Retrieve Laboratory Report and Test Results | Regional Integration Engine → FHIR Repository | Not covered | - |
| 17 | 6. FHIR Document to Central Registry | Send FHIR Document | Regional Integration Engine → Central Registry | Not covered | - |

Other example resources in this scenario:

- `FHIR/O21/GenomicsOrderMessage-ctDNA.json`
- `FHIR/ServiceRequest/ServiceRequest-ctDNA-DLIMS-WorkOrder.json`
- `FHIR/R01/TestResultsMessage-ctDNA-OmicsDSS.json`
- `FHIR/R01/ReportMessage-ctDNA-iGene-NarrativeReport.json`
- `FHIR/Document/FHIRDocumentGeneticReportBundle-ctDNA-OmicsDSS.json`
