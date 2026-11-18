# End-to-end test: Measurable Residual Disease (MRD) Monitoring - BCR-ABL1

Test cases for the NW-GMSA IG scenario [Measurable Residual Disease (MRD) Monitoring - BCR-ABL1](https://nw-gmsa.github.io/en/ExampleScenario-MRDMonitoring.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_MRDMonitoring`); FHIR Documents and other resources are for reference.

## Patients

- Rob LEEDS (9737383222)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order O21 | Order Placer - Leeds Teaching Hospitals → Regional Integration Engine | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-BCRABL.json` |
| 2 | 1. Laboratory Order (LAB-1) | Send Laboratory Order O21 | Regional Integration Engine → Order Filler - North West GLH | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-BCRABL.json` |
| 3 | 2. Work Order (LAB-4) | Send Work Order | Order Filler - North West GLH → Automation Manager - PCR Analyser | FHIR ServiceRequest | `FHIR/ServiceRequest/03-ServiceRequest-BCRABL-Cepheid-WorkOrder.json` |
| 4 | 3. Test Results (LAB-5) | Send Test Results R32 | Automation Manager - PCR Analyser → Regional Integration Engine | FHIR Message R32 | `FHIR/R32/04-TestResultsMessage-BCRABL-Cepheid.json` |
| 5 | 3. Test Results (LAB-5) | Send Test Results R32 | Regional Integration Engine → Order Filler - North West GLH | FHIR Message R32 | `FHIR/R32/04-TestResultsMessage-BCRABL-Cepheid.json` |
| 6 | 3. Test Results (LAB-5) | Send copy of Test Results using $process-message | Regional Integration Engine → FHIR Repository | FHIR Message R32 | `FHIR/R32/04-TestResultsMessage-BCRABL-Cepheid.json` |
| 7 | 4. Laboratory Report (LAB-3) | Send Laboratory Report R01 | Order Filler - North West GLH → Regional Integration Engine | FHIR Message R01 | `FHIR/R01/07-GenomicsReportMessage-BCRABL.json` |
| 8 | 5. Enhance the Laboratory Report with the discrete results | Retrieve discrete results | Regional Integration Engine → FHIR Repository | Not covered | - |
| 9 | 5. Enhance the Laboratory Report with the discrete results | Send enhanced Laboratory Report R01 | Regional Integration Engine → Order Placer - Leeds Teaching Hospitals | FHIR Message R01 | `FHIR/R01/09-GenomicsReportMessage-BCRABL-Enhanced.json` |
