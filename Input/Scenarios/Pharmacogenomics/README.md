# End-to-end test: Gene Test Before Starting a Medicine (Pharmacogenomics)

Test cases for the NW-GMSA IG scenario [Gene Test Before Starting a Medicine (Pharmacogenomics)](https://nw-gmsa.github.io/en/ExampleScenario-Pharmacogenomics.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_Pharmacogenomics`); FHIR Documents and other resources are for reference.

## Patients

- Mace Northwich (9737383311)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order | Order Placer - Liverpool Heart and Chest Hospital → Lab 1 - Order Filler - North West GLH | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-Pharmacogenomics.json` |
| 2 | 2. Sub-order (LAB-35) | Send Sub-order | Lab 1 - Order Filler - North West GLH → Lab 2 - Sub-order Filler - North West GLH | FHIR Message O21 | `FHIR/O21/02-GenomicsSubOrderMessage-Pharmacogenomics.json` |
| 3 | 3. Analytics Processing | Send genotyping data | Lab 2 - Sub-order Filler - North West GLH → Analytics Processing | Not covered | - |
| 4 | 3. Analytics Processing | Return pharmacogenomic results | Analytics Processing → Lab 2 - Sub-order Filler - North West GLH | Not covered | - |
| 5 | 4. Sub-order report (LAB-36) | Send Sub-order report | Lab 2 - Sub-order Filler - North West GLH → Lab 1 - Order Filler - North West GLH | FHIR Message R01 | `FHIR/R01/05-GenomicsSubOrderReportMessage-Pharmacogenomics.json` |
| 6 | 5. Laboratory Report (LAB-3) | Send Laboratory Report R01 | Lab 1 - Order Filler - North West GLH → Regional Integration Engine | FHIR Message R01 | `FHIR/R01/06-GenomicsReportMessage-Pharmacogenomics.json` |
| 7 | 5. Laboratory Report (LAB-3) | Send Laboratory Report R01 | Regional Integration Engine → Order Placer - Liverpool Heart and Chest Hospital | FHIR Message R01 | `FHIR/R01/06-GenomicsReportMessage-Pharmacogenomics.json` |
| 8 | 6. Enhanced Laboratory Report and FHIR Document to the central repository | Retrieve discrete results | Regional Integration Engine → FHIR Repository | Not covered | - |
| 9 | 6. Enhanced Laboratory Report and FHIR Document to the central repository | Create enhanced Laboratory Report R01 | Regional Integration Engine → Regional Integration Engine | FHIR Message R01 | `FHIR/R01/09-GenomicsReportMessage-Pharmacogenomics-Enhanced.json` |
| 10 | 6. Enhanced Laboratory Report and FHIR Document to the central repository | Send FHIR Document | Regional Integration Engine → Central Repository - UGR | FHIR Document | `FHIR/Document/10-FHIRDocumentGeneticReportBundle-Pharmacogenomics.json` |
