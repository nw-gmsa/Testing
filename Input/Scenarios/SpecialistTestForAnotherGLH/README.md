# End-to-end test: Hearing Loss Test for Another Region (Specialist Test for Another GLH)

Test cases for the NW-GMSA IG scenario [Hearing Loss Test for Another Region (Specialist Test for Another GLH)](https://nw-gmsa.github.io/en/ExampleScenario-SpecialistTestForAnotherGLH.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_SpecialistTestForAnotherGLH`); FHIR Documents and other resources are for reference.

## Patients

- Oliver CAMDEN (9737383427)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order | Order Placer - GOSH → Requesting GLH - North Thames | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-SPT.json` |
| 2 | 2. Sub-order to the North West GLH (LAB-35) | Send sub-order | Requesting GLH - North Thames → Genomic Order Management Service | FHIR Message O21 | `FHIR/O21/02-GenomicsSubOrderMessage-SPT.json` |
| 3 | 2. Sub-order to the North West GLH (LAB-35) | Route sub-order | Genomic Order Management Service → North West GLH | FHIR Message O21 | `FHIR/O21/02-GenomicsSubOrderMessage-SPT.json` |
| 4 | 3. Sub-order accepted | Send order status - accepted | North West GLH → Genomic Order Management Service | FHIR Message O51 | `FHIR/O51/04-GenomicOrderStatusMessage-SPT-Accepted.json` |
| 5 | 3. Sub-order accepted | Route order status | Genomic Order Management Service → Requesting GLH - North Thames | FHIR Message O51 | `FHIR/O51/04-GenomicOrderStatusMessage-SPT-Accepted.json` |
| 6 | 3a. Alternative: sub-order declined | Send order status - declined | North West GLH → Genomic Order Management Service | FHIR Message O51 | `FHIR/O51/06-GenomicOrderStatusMessage-SPT-Declined.json` |
| 7 | 3a. Alternative: sub-order declined | Send order status - declined after acceptance | North West GLH → Genomic Order Management Service | FHIR Message O51 | `FHIR/O51/07-GenomicOrderStatusMessage-SPT-LaterDeclined.json` |
| 8 | 4. Sub-order results (LAB-36) | Send sub-order Laboratory Report | North West GLH → Genomic Order Management Service | FHIR Message R01 | `FHIR/R01/08-GenomicsSubOrderReportMessage-SPT.json` |
| 9 | 4. Sub-order results (LAB-36) | Route sub-order Laboratory Report | Genomic Order Management Service → Requesting GLH - North Thames | FHIR Message R01 | `FHIR/R01/08-GenomicsSubOrderReportMessage-SPT.json` |
| 10 | 5. Laboratory Report (LAB-3) | Send Laboratory Report | Requesting GLH - North Thames → Order Placer - GOSH | FHIR Message R01 | `FHIR/R01/10-GenomicsReportMessage-SPT.json` |
| 11 | 6. Send to the central repository | Send Laboratory Report document | North West GLH → Central Repository - UGR | FHIR Message T02 | `FHIR/T02/11-DocumentMessage-SPT.json` |
