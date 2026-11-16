# End-to-end test: Collect Specimen - Biopsy Procedure for obtaining a specimen, part of a diagnostic pathway. Day case admission.

Test cases for the NW-GMSA IG scenario [Collect Specimen - Biopsy Procedure for obtaining a specimen, part of a diagnostic pathway. Day case admission.](https://nw-gmsa.github.io/en/ExampleScenario-BiopsyProcedure.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_BiopsyProcedure`); FHIR Documents and other resources are for reference.

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | Admission | Select Admission Forms | Nurse → Form Manager | Not covered | - |
| 2 | Admission | Pre-populate Admission Form | Form Manager → Electronic Patient Record | Not covered | - |
| 3 | Admission | Complete Admission Form. | Nurse → Patient/relative/carer | Not covered | - |
| 4 | Admission | Complete Admission Form. | Nurse → Form Manager | Not covered | - |
| 5 | Perform Biopsy | Document Procedure - Record procedure details | Consultant → Electronic Patient Record | FHIR Procedure | `FHIR/Procedure/05-13240a3b-d1db-4f1a-ad7d-b19f23967060.json` |
| 6 | Perform Biopsy | Document Procedure - Update specimen details | Nurse → Electronic Patient Record | Not covered | - |
| 7 | Perform Biopsy | Send specimen | Nurse → Diagnostic Testing | Not covered | - |
| 8 | Monitor and Discharge Patient | Monitor Patient - Update specimen details | Nurse → Electronic Patient Record | Not covered | - |
| 9 | Monitor and Discharge Patient | Discharge Patient | Nurse → Electronic Patient Record | Not covered | - |
