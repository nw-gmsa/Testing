# End-to-end test: UGR Full Pipeline

Test cases for the NW-GMSA IG scenario [UGR Full Pipeline](https://nw-gmsa.github.io/en/ExampleScenario-UGRFullPipeline.html): a ctDNA test (M4.14) for **Theon SHEFFIELD** (NHS `973 787 3858`, RHQ MRN `RHQ5948241`, iGene `200012`, see `MRN-Mapping.md`) is ordered by Sheffield Teaching Hospitals (`RHQ`), worked by Lab 1 (iGene) and Lab 2 (DLIMS with Omics DSS, Analytics Processing), reported by iGene, and sent to a central registry as a FHIR Document.

Interactions that are, or are likely to be, HL7 v2 have a v2 fixture under `V2/`. The FHIR equivalents, or FHIR-only interactions, are under `FHIR/`. The FHIR fixtures are copies of the IG's own examples, so they keep the IG's identifiers.

## Identifiers used across the steps

| Identifier | Value | Assigned by | Where |
|---|---|---|---|
| Placer order number | `1236-RHQ` | RHQ | LAB-1 ORC-2, LAB-3 ORC-2 |
| Referral (R-number) | `R26-15AY` | iGene (699X0) | Order Group Number (ORC-4 / `requisition`) |
| Test number (T-number) | `T26-59XG` | iGene (699X0) | Filler number of the Laboratory Order; placer number of the work order (LAB-4 ORC-2) |
| DLIMS order number | `D26-004512` | DLIMS | Filler number of the work order (LAB-5 ORC-3) |
| Test results number | `DSS-T26-59XG` | Omics DSS | LAB-5 OBR-3 / `DiagnosticReport.identifier` |
| Specimen | `S26-1K1Q` | iGene (699X0) | SPM-2 |
| DLIMS / Omics DSS | `DLIMS`, `OmicsDSS` | `https://fhir.nwgenomics.nhs.uk/Id/laboratory-information-system` | Work order performer; `Observation.device` (v2 OBX-18) |

## Test cases

| ID | Step | Transaction | From → To | Format | Input | Expected result |
|---|---|---|---|---|---|---|
| UGR-01 | Laboratory Order | LAB-1 | RHQ EPR → RIE → iGene | HL7 v2 `OML^O21` | `V2/O21/UGR-01-LAB1-OML_O21-RHQ-to-iGene.txt` | ACK `AA`. Converts to a `ServiceRequest` with `intent` = `order`, Order Placer Number `1236-RHQ`, requester RHQ, performer 699X0 |
| UGR-01F | Laboratory Order (FHIR) | LAB-1 | RHQ EPR → RIE | FHIR Message O21 | `FHIR/O21/UGR-01-LAB1-Bundle-GenomicsOrderMessage-ctDNA.json` | `$process-message` accepted; a copy is stored in the FHIR Repository |
| UGR-02 | Work Order | LAB-4 | iGene → DLIMS, copy to RIE | HL7 v2 `OML^O21` | `V2/O21/UGR-02-LAB4-OML_O21-iGene-to-DLIMS.txt` | ACK `AA`. Converts to a `ServiceRequest` with `intent` = `instance-order`, Order Placer Number `T26-59XG` (`iGene/ReportIdentifier`), `basedOn` the Laboratory Order (ORC-8), `performer` the DLIMS `Device` by identifier (from MSH-5). The RIE stores it in the FHIR Repository |
| UGR-02F | Work Order (FHIR) | LAB-4 | RIE → FHIR Repository | FHIR resource | `FHIR/O21/UGR-02-LAB4-ServiceRequest-ctDNA-DLIMS-WorkOrder.json` | Stored; returned by UGR-03 |
| UGR-03 | Retrieve Work Order | - | Analytics Processing → FHIR Repository | FHIR search | `GET [base]/ServiceRequest?performer:identifier=https://fhir.nwgenomics.nhs.uk/Id/laboratory-information-system\|DLIMS&intent=instance-order&status=active` | Returns the UGR-02 work order (and no `filler-order` orders). `IntegrationTest.py`'s `cdr/omicsDss` case checks this query |
| UGR-04 | Test Results | LAB-5 | DLIMS (Omics DSS) → RIE → iGene | HL7 v2 `ORU^R01` | `V2/R01/UGR-04-LAB5-ORU_R01-DLIMS-to-iGene.txt` | ACK `AA`. Converts to a [Test Results](https://nw-gmsa.github.io/en/StructureDefinition-TestResults.html) `DiagnosticReport` (`preliminary`, OBR-25 `P`) `basedOn` the work order `T26-59XG`, with the EGFR variant as a `Variant` `Observation` whose `device` is Omics DSS (OBX-18) |
| UGR-04F | Test Results (FHIR) | LAB-5 | Omics DSS → RIE, copy to FHIR Repository | FHIR Message R01 | `FHIR/R01/UGR-04-LAB5-Bundle-TestResultsMessage-ctDNA-OmicsDSS.json` | `$process-message` accepted and stored; validates against Test Results |
| UGR-05 | Laboratory Report | LAB-3 | iGene → RIE → RHQ EPR | HL7 v2 `ORU^R01` | `V2/R01/UGR-05-LAB3-ORU_R01-iGene-to-RHQ.txt` | ACK `AA`. Converts to a [Laboratory Report](https://nw-gmsa.github.io/en/StructureDefinition-LaboratoryReport.html) (`final`, `resultsInterpreter` FICTITIOUS, Morgan from OBR-32, outcome `431`) `basedOn` the Laboratory Order `1236-RHQ`. The RIE stores a copy |
| UGR-05F | Laboratory Report (FHIR) | LAB-3 | RIE → FHIR Repository | FHIR Message R01 | `FHIR/R01/UGR-05-LAB3-Bundle-ReportMessage-ctDNA-iGene-NarrativeReport.json` | `$process-message` accepted and stored; the report's `supportingInfo` links to the test results `DSS-T26-59XG` by identifier |
| UGR-06 | FHIR Document to central registry | - | RIE → central registry | HL7 v2 `MDM^T02` | `V2/T02/UGR-06-MDM_T02-RIE-to-CentralRegistry.txt` | ACK `AA`. OBX-5 (`ED`, `application/fhir+json`, Base64) carries the FHIR Document `FHIR/Document/UGR-06-Bundle-FHIRDocumentGeneticReportBundle-ctDNA-OmicsDSS.json`, which the RIE builds from the report and test results in the FHIR Repository: the merged Laboratory Report lists the variant in `result`; the Composition has the test results under Results from other laboratories. TXA-12 is the report number `T26-59XG` |

## Running

- The v2 cases (UGR-01, UGR-02, UGR-04, UGR-05, UGR-06) are registered in `IntegrationTest.py` as the `ugr_full_pipeline` group: `python3 IntegrationTest.py --group ugr_full_pipeline`.
- The FHIR message cases (UGR-01F, UGR-04F, UGR-05F) are the `ugr_full_pipeline_fhir` group.
- UGR-02F is a FHIR resource rather than a message, so it is validated with the IG rather than sent. The FHIR Document inside UGR-06 can be validated the same way: `java -jar validator_cli.jar <file> -version 4.0.1 -ig package.tgz`.
- UGR-03 is a FHIR search against the FHIR Repository (`FHIR_BASE_URL`).

## Known gaps

- The IG's `Patient-Sheffield` example has a different RHQ MRN and iGene number from `MRN-Mapping.md`, so the FHIR fixtures (UGR-01F to UGR-06) and the v2 fixtures don't carry the same local patient identifiers. The NHS number is the same.
- The IG's Laboratory Order example (UGR-01F) has no Order Placer Number, so it cannot be matched to UGR-01 by `1236-RHQ`.
- The FHIR fixtures fail IG validation only on `requisition.type` = `PGN` (Placer Group Number), which the HL7 `v2-0203` code system loaded by the validator doesn't contain. This comes from the IG's Order Group Number profile.
- iGene's current work order export to the RIE is a CSV file, not `OML^O21`. UGR-02 is the target v2 shape.
