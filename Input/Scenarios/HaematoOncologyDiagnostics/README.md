# End-to-end test: Suspected Blood Cancer - Haemato-Oncology Diagnostics

Test cases for the NW-GMSA IG scenario [Suspected Blood Cancer - Haemato-Oncology Diagnostics](https://nw-gmsa.github.io/en/ExampleScenario-HaematoOncologyDiagnostics.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_HaematoOncologyDiagnostics`); FHIR Documents and other resources are for reference.

## Patients

- Hodor TAMESIDE (9737383397)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order | Order Placer - Tameside and Glossop Integrated Care NHS FT → Haemato-Oncology Diagnostics - Manchester University NHS FT | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-HaematoOncology.json` |
| 2 | 2. Cytogenetic assessment (LAB-35 and LAB-36) | Send cytogenetics sub-order | Haemato-Oncology Diagnostics - Manchester University NHS FT → Cytogenetics Laboratory | FHIR Message O21 | `FHIR/O21/02-GenomicsSubOrderMessage-HaematoOncology-Cytogenetics.json` |
| 3 | 2. Cytogenetic assessment (LAB-35 and LAB-36) | Send cytogenetic report | Cytogenetics Laboratory → Haemato-Oncology Diagnostics - Manchester University NHS FT | FHIR Message R01 | `FHIR/R01/03-GenomicsSubOrderReportMessage-HaematoOncology-Cytogenetics.json` |
| 4 | 2. Cytogenetic assessment (LAB-35 and LAB-36) | Send cytogenetic report document | Cytogenetics Laboratory → Shared Care Record - Greater Manchester Care Record | FHIR Message T02 | `FHIR/T02/04-DocumentMessage-HaematoOncology-Cytogenetics.json` |
| 5 | 3. Molecular genomic testing, if indicated (LAB-35 and LAB-36) | Send molecular genomic sub-order | Haemato-Oncology Diagnostics - Manchester University NHS FT → Genomic Laboratory Hub - North West GLH | FHIR Message O21 | `FHIR/O21/05-GenomicsSubOrderMessage-HaematoOncology-Molecular.json` |
| 6 | 3. Molecular genomic testing, if indicated (LAB-35 and LAB-36) | Send molecular genomic report | Genomic Laboratory Hub - North West GLH → Haemato-Oncology Diagnostics - Manchester University NHS FT | FHIR Message R01 | `FHIR/R01/06-GenomicsSubOrderReportMessage-HaematoOncology-Molecular.json` |
| 7 | 3. Molecular genomic testing, if indicated (LAB-35 and LAB-36) | Send molecular genomic report document | Genomic Laboratory Hub - North West GLH → Shared Care Record - Greater Manchester Care Record | FHIR Message T02 | `FHIR/T02/07-DocumentMessage-HaematoOncology-Molecular.json` |
| 8 | 4. Combined Laboratory Report (LAB-3) | Send combined Laboratory Report | Haemato-Oncology Diagnostics - Manchester University NHS FT → Order Placer - Tameside and Glossop Integrated Care NHS FT | FHIR Message R01 | `FHIR/R01/08-GenomicsReportMessage-HaematoOncology.json` |
