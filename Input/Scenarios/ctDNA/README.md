# End-to-end test: Lung Cancer - Liquid Biopsy (ctDNA)

Test cases for the NW-GMSA IG scenario [Lung Cancer - Liquid Biopsy (ctDNA)](https://nw-gmsa.github.io/en/ExampleScenario-ctDNA.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_ctDNA`); FHIR Documents and other resources are for reference.

## Patients

- Theon SHEFFIELD (9737873858)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order O21 | Order Placer/Electronic Patient Record → Regional Integration Engine | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-ctDNA.json` |
| 2 | 1. Laboratory Order (LAB-1) | Send Laboratory Order O21 | Regional Integration Engine → Lab 1 - Order Filler LIMS | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-ctDNA.json` |
| 3 | 1. Laboratory Order (LAB-1) | Send copy of Laboratory Order using $process-message | Regional Integration Engine → FHIR Repository | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-ctDNA.json` |
| 4 | 2. Work Order (LAB-4) | Send Work Order | Lab 1 - Order Filler LIMS → Lab 2 - Automation Manager LIMS | FHIR ServiceRequest | `FHIR/ServiceRequest/04-ServiceRequest-ctDNA-DLIMS-WorkOrder.json` |
| 5 | 2. Work Order (LAB-4) | Send Work Order | Lab 1 - Order Filler LIMS → Regional Integration Engine | FHIR ServiceRequest | `FHIR/ServiceRequest/04-ServiceRequest-ctDNA-DLIMS-WorkOrder.json` |
| 6 | 2. Work Order (LAB-4) | Store Work Order | Regional Integration Engine → FHIR Repository | FHIR ServiceRequest | `FHIR/ServiceRequest/04-ServiceRequest-ctDNA-DLIMS-WorkOrder.json` |
| 7 | 3. Analytics Processing | Send sequencing data | Lab 2 - Automation Manager LIMS → Analytics Processing | Not covered | - |
| 8 | 3. Analytics Processing | Retrieve Work Order | Analytics Processing → FHIR Repository | Not covered | - |
| 9 | 4. Test Results (LAB-5) | Send Test Results R01 | Lab 2 - Automation Manager LIMS → Regional Integration Engine | FHIR Message R01 | `FHIR/R01/09-TestResultsMessage-ctDNA-OmicsDSS.json` |
| 10 | 4. Test Results (LAB-5) | Send Test Results R01 | Regional Integration Engine → Lab 1 - Order Filler LIMS | FHIR Message R01 | `FHIR/R01/09-TestResultsMessage-ctDNA-OmicsDSS.json` |
| 11 | 4. Test Results (LAB-5) | Send copy of Test Results using $process-message | Regional Integration Engine → FHIR Repository | FHIR Message R01 | `FHIR/R01/09-TestResultsMessage-ctDNA-OmicsDSS.json` |
| 12 | 5. Laboratory Report (LAB-3) | Send Laboratory Report R01 | Lab 1 - Order Filler LIMS → Regional Integration Engine | FHIR Message R01 | `FHIR/R01/12-ReportMessage-ctDNA-iGene-NarrativeReport.json` |
| 13 | 5. Laboratory Report (LAB-3) | Send Laboratory Report R01 | Regional Integration Engine → Order Placer/Electronic Patient Record | FHIR Message R01 | `FHIR/R01/12-ReportMessage-ctDNA-iGene-NarrativeReport.json` |
| 14 | 5. Laboratory Report (LAB-3) | Send copy of Laboratory Report using $process-message | Regional Integration Engine → FHIR Repository | FHIR Message R01 | `FHIR/R01/12-ReportMessage-ctDNA-iGene-NarrativeReport.json` |
| 15 | 5. Laboratory Report (LAB-3) | Send Laboratory Report document | Regional Integration Engine → Regional Shared Care Record | FHIR Message T02 | `FHIR/T02/15-DocumentMessage-ctDNA.json` |
| 16 | 6. FHIR Document to Central Registry | Retrieve Laboratory Report and Test Results | Regional Integration Engine → FHIR Repository | Not covered | - |
| 17 | 6. FHIR Document to Central Registry | Send FHIR Document | Regional Integration Engine → Central Registry | FHIR Document | `FHIR/Document/17-FHIRDocumentGeneticReportBundle-ctDNA-OmicsDSS.json` |
