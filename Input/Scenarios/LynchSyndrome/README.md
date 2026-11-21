# End-to-end test: Lynch Syndrome

Test cases for the NW-GMSA IG scenario [Lynch Syndrome](https://nw-gmsa.github.io/en/ExampleScenario-LynchSyndrome.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

The steps with an HL7 v2 message are run from the original v2 messages under `V2/<event>/` by `IntegrationTest.py` (group `scenario_LynchSyndrome`), so the FHIR is the RIE's conversion of them. The v2 messages are hand-authored and kept when the scenario is re-exported, and the IG's FHIR Messages for those steps are for reference. FHIR Messages for any other steps are run as FHIR (group `scenario_LynchSyndrome_fhir`).

## Patients

- Ned LIVERPOOL (9737383206)
- Rob LEEDS (9737383222)

## Test cases

| Step | Stage | Interaction | From → To | HL7 v2 | FHIR (IG) |
|---|---|---|---|---|---|
| 1 | 1. Pathology Order (LAB-1) | Send Pathology Order | Order Placer - Manchester University NHS FT → Order Filler and Requestor - Manchester Royal Infirmary laboratory | - | `FHIR/ServiceRequest/01-ServiceRequest-LynchReflex-OriginalOrder.json` |
| 2 | 2. Pathology to Genomics Reflex (LAB-35, LAB-36) | Send Genomic Reflex Order O21 | Order Filler and Requestor - Manchester Royal Infirmary laboratory → Regional Integration Engine | `V2/O21/02-690S0-OML_O21.txt` | `FHIR/O21/02-GenomicsOrderMessage-LynchReflex.json` |
| 3 | 2. Pathology to Genomics Reflex (LAB-35, LAB-36) | Send Genomic Reflex Order O21 | Regional Integration Engine → Order Filler - North West GLH | - | `FHIR/O21/02-GenomicsOrderMessage-LynchReflex.json` |
| 4 | 2. Pathology to Genomics Reflex (LAB-35, LAB-36) | Send Genomic Report R01 | Order Filler - North West GLH → Regional Integration Engine | `V2/R01/04-699X0-ORU_R01.txt` | `FHIR/R01/04-GenomicsReportMessage-LynchReflex.json` |
| 5 | 2. Pathology to Genomics Reflex (LAB-35, LAB-36) | Send Genomic Report R01 | Regional Integration Engine → Order Filler and Requestor - Manchester Royal Infirmary laboratory | - | `FHIR/R01/04-GenomicsReportMessage-LynchReflex.json` |
| 6 | 3. Pathology Report (LAB-3) | Send Pathology Report | Order Filler and Requestor - Manchester Royal Infirmary laboratory → Order Placer - Manchester University NHS FT | - | `FHIR/DiagnosticReport/06-DiagnosticReport-LynchReflex-Histopathology-Supplementary.json` |
| 7 | 3. Pathology Report (LAB-3) | Send copy of Genomic Report R01 | Order Filler - North West GLH → Order Placer - Manchester University NHS FT | - | `FHIR/R01/07-GenomicsReportMessage-LynchReflex-Copy.json` |
| 8 | 4. Laboratory Order (LAB-1) | Send Laboratory Order | Order Placer - Manchester University NHS FT → Order Filler - North West GLH | - | `FHIR/O21/08-GenomicsOrderMessage-LynchSyndrome.json` |
| 9 | 5. Laboratory Report (LAB-3) | Send Laboratory Report | Order Filler - North West GLH → Order Placer - Manchester University NHS FT | - | `FHIR/R01/09-GenomicsReportMessage-LynchSyndrome.json` |
| 10 | 5. Laboratory Report (LAB-3) | Send Laboratory Report document | Order Filler - North West GLH → Regional Shared Care Record | - | `FHIR/T02/10-DocumentMessage-LynchSyndrome.json` |
| 11 | 6. Send to the central repository | Send FHIR Document | Order Filler - North West GLH → Central Repository - UGR | - | `FHIR/Document/11-FHIRDocumentGeneticReportBundle2.json` |
| 12 | 7. Referral to clinical genetics (O19) | Send referral | Order Placer - Manchester University NHS FT → Referral service - eRS or Genomics England | - | `FHIR/O19/12-GenomicsReferralMessage-LynchSyndrome.json` |
| 13 | 7. Referral to clinical genetics (O19) | Route referral | Referral service - eRS or Genomics England → Clinical Genetics - Manchester Centre for Genomic Medicine | - | `FHIR/O19/12-GenomicsReferralMessage-LynchSyndrome.json` |
