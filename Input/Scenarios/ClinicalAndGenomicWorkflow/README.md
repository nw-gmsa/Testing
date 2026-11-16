# End-to-end test: Suspected Lynch Syndrome - Clinical Workflow

Test cases for the NW-GMSA IG scenario [Suspected Lynch Syndrome - Clinical Workflow](https://nw-gmsa.github.io/en/ExampleScenario-ClinicalAndGenomicWorkflow.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_ClinicalAndGenomicWorkflow`); FHIR Documents and other resources are for reference.

## Patients

- Ned LIVERPOOL (9737383206)
- Rob LEEDS (9737383222)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Suspect Lynch syndrome | Record suspected Lynch syndrome | Consultant → Electronic Patient Record | FHIR Condition | `FHIR/Condition/01-Condition-LynchSyndrome-Provisional.json` |
| 2 | 2. Request genomic diagnostic testing | Send Laboratory Order | Consultant → Genomic Diagnostic Testing - North West GLH | FHIR Message O21 | `FHIR/O21/02-GenomicsOrderMessage-LynchSyndrome.json` |
| 3 | 3. Receive the Laboratory Report | Send Laboratory Report | Genomic Diagnostic Testing - North West GLH → Consultant | FHIR Message R01 | `FHIR/R01/03-GenomicsReportMessage-LynchSyndrome.json` |
| 4 | 4. Confirm Lynch syndrome | Update Lynch syndrome to confirmed | Consultant → Electronic Patient Record | FHIR Condition | `FHIR/Condition/04-c8f82825-e4cb-4e1f-b728-3fd2808e93db.json` |
| 5 | 5. Refer the family to clinical genetics | Send referral | Consultant → Clinical Genetics | FHIR Message O19 | `FHIR/O19/05-GenomicsReferralMessage-LynchSyndrome.json` |
| 6 | 6. Record family history | Record family history - son | Clinical Genetics → Family history system - for example NDRS | FHIR FamilyMemberHistory | `FHIR/FamilyMemberHistory/06-074ea905-8d91-452c-af3c-15b5b860fdb2.json` |
| 7 | 6. Record family history | Record family history - mother | Clinical Genetics → Family history system - for example NDRS | FHIR FamilyMemberHistory | `FHIR/FamilyMemberHistory/07-c76b8bc2-ec36-4ce1-a2ea-8c57215115e2.json` |
