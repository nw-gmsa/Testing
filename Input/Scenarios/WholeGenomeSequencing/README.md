# End-to-end test: Whole Genome Sequencing for a Rare Condition

Test cases for the NW-GMSA IG scenario [Whole Genome Sequencing for a Rare Condition](https://nw-gmsa.github.io/en/ExampleScenario-WholeGenomeSequencing.html), exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: change the IG and re-export.

All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` (group `scenario_WholeGenomeSequencing`); FHIR Documents and other resources are for reference.

## Patients

- Gilly BROUGH (9737383362)
- Six EDITESTPATIENT (9999999514)
- Thirteen EDITESTPATIENT (9999999581)

## Test cases

| Step | Stage | Interaction | From → To | Format | File |
|---|---|---|---|---|---|
| 1 | 1. Laboratory Order (LAB-1, O19) | Submit referral | Order Placer - NHS Trust → Genomics England | FHIR Message O19 | `FHIR/O19/01-GenomicsOrderMessage-WGS-Referral.json` |
| 2 | 1. Laboratory Order (LAB-1, O19) | Route Laboratory Order | Genomics England → Requesting Genomic Laboratory - RGL | FHIR Message O19 | `FHIR/O19/01-GenomicsOrderMessage-WGS-Referral.json` |
| 3 | 2. Sub-orders (LAB-35) | Send sub-order - Proband | Requesting Genomic Laboratory - RGL → Sequencing Genomic Laboratory - SGL | FHIR Message O21 | `FHIR/O21/03-dWGS-Trio-r26000000203-p26000000104.json` |
| 4 | 2. Sub-orders (LAB-35) | Send sub-order - Family Member | Requesting Genomic Laboratory - RGL → Sequencing Genomic Laboratory - SGL | FHIR Message O21 | `FHIR/O21/04-dWGS-Trio-r26000000203-p26000000105.json` |
| 5 | 2. Sub-orders (LAB-35) | Send sub-order - Family Member | Requesting Genomic Laboratory - RGL → Sequencing Genomic Laboratory - SGL | FHIR Message O21 | `FHIR/O21/05-dWGS-Trio-r26000000203-p26000000106.json` |
| 6 | 3. Sequencing (LAB-4 and LAB-5) | Send Work Order | Sequencing Genomic Laboratory - SGL → Sequencer | Not covered | - |
| 7 | 3. Sequencing (LAB-4 and LAB-5) | Upload sequence data | Sequencing Genomic Laboratory - SGL → Genomics England | Not covered | - |
| 8 | 4. Sub-order Results (LAB-36) | Make results available | Genomics England → Requesting Genomic Laboratory - RGL | Not covered | - |
| 9 | 5. Participant Results to Central Registry | Retrieve participant results | Integration Engine → Genomics England | Not covered | - |
| 10 | 5. Participant Results to Central Registry | Send FHIR Document | Integration Engine → Central Registry | Not covered | - |
| 11 | 6. Laboratory Report (LAB-3) | Send Laboratory Report | Requesting Genomic Laboratory - RGL → Order Placer - NHS Trust | FHIR Message R01 | `FHIR/R01/11-GenomicsReportMessage-WGS-Referral.json` |

Other example resources in this scenario:

- `FHIR/Group/FamilyGeneticGroup-dWGS-Trio-r26000000203.json`
