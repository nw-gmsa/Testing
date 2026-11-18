# End-to-end test: Chimerism Monitoring After a Stem Cell Transplant

Test cases for the NW-GMSA IG scenario [Chimerism Monitoring After a Stem Cell Transplant](https://nw-gmsa.github.io/en/ExampleScenario-ChimerismMonitoring.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_ChimerismMonitoring`); FHIR Documents and other resources are for reference.

## Patients

- Ned LIVERPOOL (9737383206)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order | Order Placer - Cancer Centre → Order Filler - H&I laboratory | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-Chimerism.json` |
| 2 | 2. Laboratory Report (LAB-3) | Send Laboratory Report | Order Filler - H&I laboratory → Order Placer - Cancer Centre | FHIR Message R01 | `FHIR/R01/02-GenomicsReportMessage-Chimerism.json` |
