# End-to-end test: Lung Cancer - Liquid Biopsy (ctDNA)

Test cases for the NW-GMSA IG scenario [Lung Cancer - Liquid Biopsy (ctDNA)](https://nw-gmsa.github.io/en/ExampleScenario-ctDNA.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_ctDNA`); FHIR Documents and other resources are for reference.

## Patients

- Theon SHEFFIELD (9737873858)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order O21 | Order Placer/Electronic Patient Record → Regional Integration Engine | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-ctDNA-OrderPlacer.json` |
| 2 | 1. Laboratory Order (LAB-1) | Send Laboratory Order O21 | Regional Integration Engine → Lab 1 - Order Filler LIMS | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-ctDNA-OrderPlacer.json` |
| 3 | 1. Laboratory Order (LAB-1) | Send copy of Laboratory Order using $process-message | Regional Integration Engine → FHIR Repository | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-ctDNA-OrderPlacer.json` |
| 4 | 2. Filler Order Management (LAB-2) | Send copy of Laboratory Order O21 - LAB-2 | Lab 1 - Order Filler LIMS → Regional Integration Engine | FHIR Message O21 | `FHIR/O21/04-GenomicsOrderMessage-ctDNA.json` |
| 5 | 2. Filler Order Management (LAB-2) | Send copy of Laboratory Order O21 - LAB-2 | Regional Integration Engine → Order Placer Manager | FHIR Message O21 | `FHIR/O21/04-GenomicsOrderMessage-ctDNA.json` |
| 6 | 3. Work Order (LAB-4) | Send Work Order | Lab 1 - Order Filler LIMS → Lab 2 - Automation Manager LIMS | FHIR ServiceRequest | `FHIR/ServiceRequest/06-ServiceRequest-ctDNA-DLIMS-WorkOrder.json` |
| 7 | 3. Work Order (LAB-4) | Send Work Order | Lab 1 - Order Filler LIMS → Regional Integration Engine | FHIR ServiceRequest | `FHIR/ServiceRequest/06-ServiceRequest-ctDNA-DLIMS-WorkOrder.json` |
| 8 | 3. Work Order (LAB-4) | Store Work Order | Regional Integration Engine → FHIR Repository | FHIR ServiceRequest | `FHIR/ServiceRequest/06-ServiceRequest-ctDNA-DLIMS-WorkOrder.json` |
| 9 | 4. Analytics Processing | Send sequencing data | Lab 2 - Automation Manager LIMS → Analytics Processing | Not covered | - |
| 10 | 4. Analytics Processing | Retrieve Work Order | Analytics Processing → FHIR Repository | Not covered | - |
| 11 | 5. Test Results (LAB-5) | Send Test Results R01 | Lab 2 - Automation Manager LIMS → Regional Integration Engine | FHIR Message R01 | `FHIR/R01/11-TestResultsMessage-ctDNA-OmicsDSS.json` |
| 12 | 5. Test Results (LAB-5) | Send Test Results R01 | Regional Integration Engine → Lab 1 - Order Filler LIMS | FHIR Message R01 | `FHIR/R01/11-TestResultsMessage-ctDNA-OmicsDSS.json` |
| 13 | 5. Test Results (LAB-5) | Send copy of Test Results using $process-message | Regional Integration Engine → FHIR Repository | FHIR Message R01 | `FHIR/R01/11-TestResultsMessage-ctDNA-OmicsDSS.json` |
| 14 | 6. Laboratory Report (LAB-3) | Send Laboratory Report R01 | Lab 1 - Order Filler LIMS → Regional Integration Engine | FHIR Message R01 | `FHIR/R01/14-ReportMessage-ctDNA-iGene-NarrativeReport.json` |
| 15 | 6. Laboratory Report (LAB-3) | Send Laboratory Report R01 | Regional Integration Engine → Order Placer/Electronic Patient Record | FHIR Message R01 | `FHIR/R01/14-ReportMessage-ctDNA-iGene-NarrativeReport.json` |
| 16 | 6. Laboratory Report (LAB-3) | Send copy of Laboratory Report R01 without the report | Regional Integration Engine → Order Placer Manager | FHIR Message R01 | `FHIR/R01/16-ReportMessage-ctDNA-iGene-OrderPlacerManager.json` |
| 17 | 6. Laboratory Report (LAB-3) | Send copy of Laboratory Report using $process-message | Regional Integration Engine → FHIR Repository | FHIR Message R01 | `FHIR/R01/14-ReportMessage-ctDNA-iGene-NarrativeReport.json` |
| 18 | 6. Laboratory Report (LAB-3) | Send Laboratory Report document | Regional Integration Engine → Regional Shared Care Record | FHIR Message T02 | `FHIR/T02/18-DocumentMessage-ctDNA.json` |
| 19 | 6. Laboratory Report (LAB-3) | Send Laboratory Report document | Regional Integration Engine → Central Registry | FHIR Message T02 | `FHIR/T02/18-DocumentMessage-ctDNA.json` |
| 20 | 7. Enhanced Laboratory Report and FHIR Document to Central Registry | Retrieve Laboratory Report and Test Results | Regional Integration Engine → FHIR Repository | Not covered | - |
| 21 | 7. Enhanced Laboratory Report and FHIR Document to Central Registry | Create enhanced Laboratory Report R01 | Regional Integration Engine → Regional Integration Engine | FHIR Message R01 | `FHIR/R01/21-ReportMessage-ctDNA-iGene-Enhanced.json` |
| 22 | 7. Enhanced Laboratory Report and FHIR Document to Central Registry | Send FHIR Document | Regional Integration Engine → Central Registry | FHIR Document | `FHIR/Document/22-FHIRDocumentGeneticReportBundle-ctDNA-OmicsDSS.json` |
