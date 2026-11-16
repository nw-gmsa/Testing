# End-to-end test: Rapid Genetic Testing in Pregnancy (Rapid Prenatal Exome Sequencing)

Test cases for the NW-GMSA IG scenario [Rapid Genetic Testing in Pregnancy (Rapid Prenatal Exome Sequencing)](https://nw-gmsa.github.io/en/ExampleScenario-RapidPrenatalExomeSequencing.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_RapidPrenatalExomeSequencing`); FHIR Documents and other resources are for reference.

## Patients

- Baby WIGAN (R0A-F26-0042)
- Daniel WIGAN (9737383419)
- Imogen WIGAN (9737383400)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1) | Send Laboratory Order | Fetal Medicine Unit - Manchester University NHS FT → Home GLH - North West | FHIR Message O21 | `FHIR/O21/01-GenomicsOrderMessage-RPX.json` |
| 2 | 2. First-line tests at the home GLH | Perform first-line tests | Home GLH - North West → Home GLH - North West | Not covered | - |
| 3 | 2a. Alternative: cause found by first-line tests | Send Laboratory Report | Home GLH - North West → Fetal Medicine Unit - Manchester University NHS FT | FHIR Message R01 | `FHIR/R01/03-GenomicsReportMessage-RPX-FirstLine.json` |
| 4 | 3. Sub-order to the testing GLH (LAB-35) | Send sub-order | Home GLH - North West → Genomic Order Management Service | FHIR Message O21 | `FHIR/O21/04-GenomicsSubOrderMessage-RPX.json` |
| 5 | 3. Sub-order to the testing GLH (LAB-35) | Route sub-order | Genomic Order Management Service → Testing GLH - North Thames | FHIR Message O21 | `FHIR/O21/04-GenomicsSubOrderMessage-RPX.json` |
| 6 | 4. Sub-order accepted | Send order status - accepted | Testing GLH - North Thames → Genomic Order Management Service | FHIR Message O51 | `FHIR/O51/06-GenomicOrderStatusMessage-RPX-Accepted.json` |
| 7 | 4. Sub-order accepted | Route order status | Genomic Order Management Service → Home GLH - North West | FHIR Message O51 | `FHIR/O51/06-GenomicOrderStatusMessage-RPX-Accepted.json` |
| 8 | 4a. Alternative: sub-order declined | Send order status - declined | Testing GLH - North Thames → Genomic Order Management Service | FHIR Message O51 | `FHIR/O51/08-GenomicOrderStatusMessage-RPX-Declined.json` |
| 9 | 4a. Alternative: sub-order declined | Route order status | Genomic Order Management Service → Home GLH - North West | FHIR Message O51 | `FHIR/O51/08-GenomicOrderStatusMessage-RPX-Declined.json` |
| 10 | 4a. Alternative: sub-order declined | Tell the requesting clinician | Home GLH - North West → Fetal Medicine Unit - Manchester University NHS FT | FHIR Message O51 | `FHIR/O51/10-GenomicOrderStatusMessage-RPX-NotTested.json` |
| 11 | 5. Sub-order results (LAB-36) | Send sub-order Laboratory Report | Testing GLH - North Thames → Genomic Order Management Service | FHIR Message R01 | `FHIR/R01/11-GenomicsSubOrderReportMessage-RPX.json` |
| 12 | 5. Sub-order results (LAB-36) | Route sub-order Laboratory Report | Genomic Order Management Service → Home GLH - North West | FHIR Message R01 | `FHIR/R01/11-GenomicsSubOrderReportMessage-RPX.json` |
| 13 | 6. Laboratory Report (LAB-3) | Send Laboratory Report | Home GLH - North West → Fetal Medicine Unit - Manchester University NHS FT | FHIR Message R01 | `FHIR/R01/13-GenomicsReportMessage-RPX.json` |
| 14 | 7. Send to the central repository | Send Laboratory Report document | Home GLH - North West → Central Repository - UGR | FHIR Message T02 | `FHIR/T02/14-DocumentMessage-RPX.json` |
| 15 | 8. Referral to clinical genetics (O19) | Send referral | Fetal Medicine Unit - Manchester University NHS FT → Referral service - eRS or Genomics England | FHIR Message O19 | `FHIR/O19/15-GenomicsReferralMessage-RPX.json` |
| 16 | 8. Referral to clinical genetics (O19) | Route referral | Referral service - eRS or Genomics England → Clinical Genetics - Manchester Centre for Genomic Medicine | FHIR Message O19 | `FHIR/O19/15-GenomicsReferralMessage-RPX.json` |
