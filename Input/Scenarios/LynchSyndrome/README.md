# End-to-end test: Lynch Syndrome

Test cases for the NW-GMSA IG scenario [Lynch Syndrome](https://nw-gmsa.github.io/en/ExampleScenario-LynchSyndrome.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

The steps with an HL7 v2 message are run from the original v2 messages under `V2/<event>/` by `IntegrationTest.py` (group `scenario_LynchSyndrome`), so the FHIR is the RIE's conversion of them. The v2 messages are hand-authored and kept when the scenario is re-exported, and the IG's FHIR Messages for those steps are for reference. FHIR Messages for any other steps are run as FHIR (group `scenario_LynchSyndrome_fhir`).

## Patients

- Ned LIVERPOOL (9737383206)
- Rob LEEDS (9737383222)

## Test cases

| Step | Stage | Interaction | From → To | HL7 v2 | FHIR (IG) |
|---|---|---|---|---|---|
| 1 | 1. Pathology to Genomics Reflex (LAB-35, LAB-36) | Send Genomic Reflex Order O21 | Order Filler and Requestor - Manchester Royal Infirmary laboratory → Regional Integration Engine | `V2/O21/01-690S0-OML_O21.txt` | `FHIR/O21/01-GenomicsOrderMessage-LynchReflex.json` |
| 2 | 1. Pathology to Genomics Reflex (LAB-35, LAB-36) | Send Genomic Reflex Order O21 | Regional Integration Engine → Order Filler - North West GLH | - | `FHIR/O21/01-GenomicsOrderMessage-LynchReflex.json` |
| 3 | 1. Pathology to Genomics Reflex (LAB-35, LAB-36) | Send Genomic Report R01 | Order Filler - North West GLH → Regional Integration Engine | `V2/R01/03-699X0-ORU_R01.txt` | `FHIR/R01/03-GenomicsReportMessage-LynchReflex.json` |
| 4 | 1. Pathology to Genomics Reflex (LAB-35, LAB-36) | Send Genomic Report R01 | Regional Integration Engine → Order Filler and Requestor - Manchester Royal Infirmary laboratory | - | `FHIR/R01/03-GenomicsReportMessage-LynchReflex.json` |
| 5 | 2. Laboratory Order (LAB-1) | Send Laboratory Order | Order Placer - Manchester University NHS FT → Order Filler - North West GLH | - | `FHIR/O21/05-GenomicsOrderMessage-LynchSyndrome.json` |
| 6 | 3. Laboratory Report (LAB-3) | Send Laboratory Report | Order Filler - North West GLH → Order Placer - Manchester University NHS FT | - | `FHIR/R01/06-GenomicsReportMessage-LynchSyndrome.json` |
| 7 | 3. Laboratory Report (LAB-3) | Send Laboratory Report document | Order Filler - North West GLH → Regional Shared Care Record | - | `FHIR/T02/07-DocumentMessage-LynchSyndrome.json` |
| 8 | 4. Send to the central repository | Send FHIR Document | Order Filler - North West GLH → Central Repository - UGR | - | `FHIR/Document/08-FHIRDocumentGeneticReportBundle2.json` |
| 9 | 5. Referral to clinical genetics (O19) | Send referral | Order Placer - Manchester University NHS FT → Referral service - eRS or Genomics England | - | `FHIR/O19/09-GenomicsReferralMessage-LynchSyndrome.json` |
| 10 | 5. Referral to clinical genetics (O19) | Route referral | Referral service - eRS or Genomics England → Clinical Genetics - Manchester Centre for Genomic Medicine | - | `FHIR/O19/09-GenomicsReferralMessage-LynchSyndrome.json` |
