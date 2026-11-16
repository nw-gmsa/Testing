# End-to-end test: Inherited Breast Cancer (BRCA)

Test cases for the NW-GMSA IG scenario [Inherited Breast Cancer (BRCA)](https://nw-gmsa.github.io/en/ExampleScenario-BreastCancer.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_BreastCancer`); FHIR Documents and other resources are for reference.

## Patients

- Lysa BUXTON (9737383338)
- Margaery CONGLETON (9737383281)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order | Order Placer - East Cheshire NHS Trust → Order Filler - North West GLH | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-BreastCancer.json` |
| 2 | 2. Laboratory Report (LAB-3) | Send Laboratory Report | Order Filler - North West GLH → Order Placer - East Cheshire NHS Trust | FHIR Message R01 | `FHIR/R01/02-GenomicsReportMessage-BreastCancer.json` |
| 3 | 2. Laboratory Report (LAB-3) | Send Laboratory Report document | Order Filler - North West GLH → Regional Shared Care Record | FHIR Message T02 | `FHIR/T02/03-DocumentMessage-BreastCancer.json` |
| 4 | 3. Send to the central repository | Send FHIR Document | Order Filler - North West GLH → Central Repository - UGR | FHIR Document | `FHIR/Document/04-FHIRDocumentGeneticReportBundle-BreastCancer.json` |
| 5 | 4. Referral to clinical genetics (O19) | Send referral | Order Placer - East Cheshire NHS Trust → Referral service - eRS or Genomics England | FHIR Message O19 | `FHIR/O19/05-GenomicsReferralMessage-BreastCancer.json` |
| 6 | 4. Referral to clinical genetics (O19) | Route referral | Referral service - eRS or Genomics England → Clinical Genetics - Manchester Centre for Genomic Medicine | FHIR Message O19 | `FHIR/O19/05-GenomicsReferralMessage-BreastCancer.json` |
