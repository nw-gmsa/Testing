# End-to-end test: Whole Genome Sequencing

Test cases for the NW-GMSA IG scenario [Whole Genome Sequencing](https://nw-gmsa.github.io/en/ExampleScenario-WholeGenomeSequencing.html), using the dWGS Trio referral `r26000000203` (Test Directory `R27.3`):

| Participant | NHS Number | NGIS participant id | Role |
|---|---|---|---|
| Gilly BROUGH | `973 738 3362` | `p26000000104` | Proband |
| Thirteen EDITESTPATIENT | `999 999 9581` | `p26000000105` | Family member |
| Six EDITESTPATIENT | `999 999 9514` | `p26000000106` | Family member |

The referring Trust is North Cumbria (`RNN`, proband MRN `RNN1799141`). The Requesting Genomic Laboratory (RGL) is NE&Y Genomics, Northern Genetics Service (`699N0`); the Sequencing Genomic Laboratory (SGL) is NW Genomics (`699X0`, iGene). The NGIS identifiers are assigned by Genomics England (`8J834`).

Many of these interactions are national (Genomics England TOMS, CIP-API and Interpretation Portal) or internal to a laboratory, and are not covered by the IG. Those steps are listed for completeness, with how they could be checked.

## Test cases

| ID | Step | Transaction | From → To | Format | Input | Expected result |
|---|---|---|---|---|---|---|
| WGS-01 | Laboratory Order (proband) | LAB-1 | RNN EPR → RGL | HL7 v2 `OML^O21` | `V2/O21/WGS-01-LAB1-OML_O21-RNN-to-RGL.txt` | ACK `AA`. Converts to a `ServiceRequest` for the proband with Order Placer Number `RNN26-0042`, Order Group Number `r26000000203` (ORC-4), Family Structure `Trio` and Participant Type `Proband` (OBX) |
| WGS-01R | Referral registered with Genomics England | LAB-1 | RGL → Genomics England (TOMS) | Not FHIR (TOMS) | Illustrated by `FHIR/Referral/WGS-01-ServiceRequest-dWGS-Trio-r26000000203-Referral.json` and `FHIR/Referral/WGS-01-Group-FamilyGeneticGroup-dWGS-Trio-r26000000203.json` | Not exchanged. Both validate against the IG: an original order (`intent` = `original-order`) whose subject is the family and whose Order Filler Number is the NGIS referral_id |
| WGS-02 | Sub-orders, one per participant | LAB-35 | RGL → SGL (RIE) | Digital manifest CSV → FHIR Message O21 → HL7 v2 | `Input/dWGS.csv` rows for `r26000000203`; `Input/FHIR/O21/dWGS_r26000000203_p26000000104.json`, `..._p26000000105.json`, `..._p26000000106.json` | Covered by the existing `dwgs` group: each `$process-message` accepted, `intent` = `filler-order`, `requisition` `r26000000203`, converted to iGene `ORM^O01` |
| WGS-03 | Work order to the sequencer | LAB-4 | SGL → sequencer | Internal | - | Not covered |
| WGS-04 | Sequence data upload and sub-order results | LAB-36 | SGL → Genomics England → RGL | Not FHIR (CIP-API / Interpretation Portal) | - | Not covered. The RGL retrieves each participant's results by NGIS referral_id and participant id |
| WGS-05 | Participant results to central registry | - | Integration engine → central registry | HL7 v2 `MDM^T02` | `V2/T02/WGS-05-MDM_T02-IntegrationEngine-to-CentralRegistry.txt` | ACK `AA`. OBX-5 (`ED`, `application/fhir+json`, Base64) carries the FHIR Document `FHIR/Document/WGS-05-Document-p26000000104.json`, which the integration engine builds from the proband's results in the CIP-API: a [Test Results](https://nw-gmsa.github.io/en/StructureDefinition-TestResults.html) `DiagnosticReport` `basedOn` the proband's sub-order `4000000004`, with the variant as a `Variant` `Observation`. One message is expected for each participant; only the proband's is provided |
| WGS-06 | Laboratory Report (family) | LAB-3 | RGL → RNN EPR | HL7 v2 `ORU^R01` | `V2/R01/WGS-06-LAB3-ORU_R01-RGL-to-RNN.txt` | ACK `AA`. Converts to a [Laboratory Report](https://nw-gmsa.github.io/en/StructureDefinition-LaboratoryReport.html) (`final`, `resultsInterpreter` FICTITIOUS, Quentin from OBR-32, outcome `321`) `basedOn` `RNN26-0042`. Logically this is a report on the whole family; the v2 message is sent for the proband |

## Running

- The v2 cases (WGS-01, WGS-05, WGS-06) are registered in `IntegrationTest.py` as the `wgs_full_pipeline` group: `python3 IntegrationTest.py --group wgs_full_pipeline`.
- WGS-02 is the existing `dwgs` group: `python3 IntegrationTest.py --group dwgs`.
- WGS-01R is FHIR resources rather than a message, so it is validated with the IG rather than sent. The FHIR Document inside WGS-05 can be validated the same way: `java -jar validator_cli.jar <file> -version 4.0.1 -ig package.tgz`.

## Known gaps

- WGS-01 and WGS-06 are sent to and from the RGL (NE&Y Genomics), so they test the message shape rather than a NW system.
- Only the proband's participant results message is provided (WGS-05). Its Specimen omits the `container`, which in the sub-order has no device extension and so fails the IG's Specimen profile.
- The FHIR fixtures fail IG validation only on `requisition.type` = `PGN` (Placer Group Number), which the HL7 `v2-0203` code system loaded by the validator doesn't contain. This comes from the IG's Order Group Number profile.
- The SCN2A variant is fictitious test data.
