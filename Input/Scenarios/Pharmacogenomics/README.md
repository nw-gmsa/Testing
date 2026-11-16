# End-to-end test: Gene Test Before Starting a Medicine (Pharmacogenomics)

Test cases for the NW-GMSA IG scenario [Gene Test Before Starting a Medicine (Pharmacogenomics)](https://nw-gmsa.github.io/en/ExampleScenario-Pharmacogenomics.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_Pharmacogenomics`); FHIR Documents and other resources are for reference.

## Patients

- Mace Northwich (9737383311)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order | Order Placer - Liverpool Heart and Chest Hospital → Order Filler - North West GLH | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-Pharmacogenomics.json` |
| 2 | 2. Laboratory Report (LAB-3) | Send Laboratory Report | Order Filler - North West GLH → Order Placer - Liverpool Heart and Chest Hospital | FHIR Message R01 | `FHIR/R01/02-GenomicsReportMessage-Pharmacogenomics.json` |
| 3 | 3. Send to the central repository | Send FHIR Document | Order Filler - North West GLH → Central Repository - UGR | FHIR Document | `FHIR/Document/03-FHIRDocumentGeneticReportBundle-Pharmacogenomics.json` |
