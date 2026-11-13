# Master List: Fictitious Practitioners

Every practitioner in this repository's fixtures, and in the NW-GMSA implementation guide examples, should come from this list. Real practitioners' names and professional codes must not be used, and this repository is public.

Each practitioner has at most one professional code, which is one of:

| Code type | Who | FHIR `Identifier.system` | HL7 v2 XCN-9 / NDL assigning authority | Format used here |
|---|---|---|---|---|
| GMC | Doctors (General Medical Council) | `https://fhir.hl7.org.uk/Id/gmc-number` | `GMC` | `C` + 7 digits, fictitious range `C9000101`-`C9000199` for new entries |
| GMP | General practitioners (GP code) | `https://fhir.hl7.org.uk/Id/gmp-number` | `GMP` | `G` + 7 digits, fictitious range `G9000101`-`G9000199` |
| HCPC | Clinical scientists and other Health and Care Professions Council registrants | `https://fhir.hl7.org.uk/Id/hcpc-number` | `HCPC` | `CS` + 5 digits, fictitious range `CS90001`-`CS90099` |
| Local | A system's own user code, e.g. an iGene user | The system's own URI | The system's own code | `ZZ_` + 3 letters for new entries |
| None | No code, e.g. only a display name or a role | - | - | - |
{:.grid}

In HL7 v2 the code goes in XCN-1 (or NDL-1 for OBR-32), with the code type in XCN-9, e.g. `C3456789^Darwin^Samuel^^^Dr^^^GMC`. In FHIR it is `PractitionerRole.practitioner.identifier` (or the `identifier` of a reference such as `DiagnosticReport.resultsInterpreter`).

**Caveats:**
- The new fictitious ranges (`C90001xx`, `G90001xx`, `CS9xxxx`) are chosen to be outside numbers seen in real use, but are not guaranteed never to be issued. They are for test data only.
- `C9999998` and `C9999999` are placeholder GMC codes taken from published example data. `9999999998` and `9999999999` are NHS England placeholder SDS user ids.
- The SDS user ids `3208835210` and `2441541066` come from NHS England's published Non-WGS Test Order Form examples and are kept as published.
- `FICTITIOUS, <given name>` is the naming style used in the implementation guide's own examples, so a reader can tell at a glance the person is not real.

## Practitioners already used in examples

| Display name | Code type | Code | Organisation (ODS) | Role in the examples | Used in |
|---|---|---|---|---|---|
| Dr Samuel Darwin | GMC | `C3456789` | `R0A` | Ordering provider | IG HL7 v2 page and order examples; `Input/V2/O21/OML_O21_R0A_R125.txt`, `Input/V2/O21/OML_O21_RPY.txt`, `Input/V2/O51/*` |
| FICTITIOUS, Ralph | GMC | `C1234567` | `699X0` | Results interpreter and report attester | IG FHIR Document examples (Pharmacogenomics, Somatic, WGS) |
| FICTITIOUS, Hester | GMC | `C2345671` | `RBQ` | Requester | IG Pharmacogenomics examples |
| FICTITIOUS, Imogen | GMC | `C3456712` | `RBV` | Requester | IG Somatic examples |
| FICTITIOUS, Owen | GMC | `C4567123` | `RM3` | Requester | IG WGS (external laboratory) examples |
| Sheffield Lung Doctor | GMC | `C9999998` | `RHQ` | Requester | IG ctDNA examples |
| Lucy Hale | GMC | `C9999999` | `RBV` | Requester | `Input/FHIR/**/UKCore-Bundle-MichaelJonesRequest-*.json` (UK Core example) |
| Dr Indiana Jones | GMC | `1234567` | - | Ordering provider | `Input/V2/R01/WALES_ORU_R01_FULL.txt` |
| FICTITIOUS, Morgan | HCPC (iGene user `ZZ_MOR`) | `CS90001` | `699X0` | Results interpreter (clinical scientist) and ordering provider | IG ctDNA examples; `Input/NorthEnglandctDNA100.csv` and the ctDNA `ORU^R01` messages (OBR-32) |
| Dr Hazel Smith | Local (SDS user id) | `9999999998` | `RAX01` | Requester | `Input/FHIR/**/Bundle-NonWGSTestOrderForm-*.json`; `Input/V2/O21/OML_O21_RPY.txt` (`X26`) |
| Dr Gene Smith | Local (SDS user id) | `9999999999` | `RGT01` | Requester | `Input/FHIR/**/Bundle-NonWGSTestOrderForm-Example.json` |
| Dr Anna Lane | Local (SDS user id) | `9999999998` | `RAX01` | Requester | `Input/FHIR/**/Bundle-NonWGSTestOrderForm-CancerSolidTumor-Example.json` |
| Dr James Taylor | Local (SDS user id) | `9999999998` | `RAX01` | Requester | `Input/FHIR/**/Bundle-NonWGSTestOrderForm-CancerSolidTumor-Example.json` |
| Dr Lois Lane | Local (SDS user id) | `9999999999`, `3208835210`, `2441541066` | `RAX`, `RAX01`, `RYJ02` | Requester | `Input/FHIR/**/Bundle-NonWGS*-Example*.json` |
| Dr Clinician | Local | `Dr_Clinician` | Various | Ordering provider | `Input/NEYctDNA.csv`, `Input/StarLIMSSampleData.csv`, `Input/V2/O21/*` |
| TEST TESTPROVIDER | Local (NIST test provider) | `ZZZ57422` | - | Ordering provider | `Input/V2/O01/EPIC-Raw.txt` |
| ACME SUPER USER | None | - | - | Result interpreter | `Input/V2/R01/WALES_ORU_R01_FULL.txt` |
| Result INTERPRETER | None | - | `699X0` | Results interpreter (role only) | IG report examples |
| Duty Scientist on behalf of NEYGLH Medical | None | - | `699N0` | Requester of dWGS sub-orders (role only) | IG and `Input/FHIR/O21/dWGS_*.json` |
{:.grid}

## Fictitious practitioners for replacing possibly real ones

Use these when a fixture's practitioner may be a real person (see the next section). Pick one with the same code type and a similar role, and use it consistently for every fixture that had the same original practitioner.

| Display name | Prefix | Code type | Code | Organisation (ODS) | Typical role |
|---|---|---|---|---|---|
| FICTITIOUS, Alice | Dr | GMC | `C9000101` | `R0A` | Consultant haematologist, ordering provider |
| FICTITIOUS, Bernard | Dr | GMC | `C9000102` | `REN` | Consultant oncologist, ordering provider |
| FICTITIOUS, Clara | Dr | GMC | `C9000103` | `RBS` | Consultant paediatrician, ordering provider |
| FICTITIOUS, Desmond | Dr | GMC | `C9000104` | `RHQ` | Consultant respiratory physician, ordering provider |
| FICTITIOUS, Esther | Dr | GMC | `C9000105` | `RTD` | Consultant clinical geneticist, ordering provider |
| FICTITIOUS, Felix | Mr | GMC | `C9000106` | `RR8` | Consultant surgeon, ordering provider |
| FICTITIOUS, Gwen | Dr | GMP | `G9000101` | `P84001` | General practitioner, ordering provider |
| FICTITIOUS, Harold | Dr | GMP | `G9000102` | `B82033` | General practitioner, ordering provider |
| FICTITIOUS, Priya |  | HCPC | `CS90002` | `699X0` | Clinical scientist, results interpreter |
| FICTITIOUS, Quentin |  | HCPC | `CS90003` | `699N0` | Clinical scientist, results interpreter |
| FICTITIOUS, Rosa |  | HCPC | `CS90004` | `699X0` | Clinical scientist, cytogenetics results interpreter |
| FICTITIOUS, Dana |  | Local (iGene user) | `ZZ_DAN` | `699X0` | Laboratory user, results interpreter |
| FICTITIOUS, Eli |  | Local (iGene user) | `ZZ_ELI` | `699X0` | Laboratory user, ordering provider on internal orders |
| FICTITIOUS, Nell |  | None | - | - | Name only, no code |
{:.grid}

## Replaced practitioners

These fictitious practitioners replaced practitioners in the fixtures who may have been real people. They are listed with the fixtures that now use them. Where a fixture is generated from another (for example the `ctDNA_*.txt` messages from `Input/NorthEnglandctDNA100.csv`), the source and the generated files were changed together.

| Display name | Code type | Code | Fixtures (fields) |
|---|---|---|---|
| Dr Morgan FICTITIOUS | Local (iGene user) | `ZZ_MOR` | `Input/NorthEnglandctDNA100.csv` (`OrderingProvider*`); `Input/ctDNA/*.txt`, `Input/V2/R01/ctdna*.txt`, `Input/V2/R01/ORU_R01_*.txt`, `Input/V2/iGeneR01-*.txt` (OBR-32); notebooks 04 and 06; email `morgan.fictitious@example.nhs.uk` |
| Dr Ruben FICTITIOUS | Local (iGene user) | `ZZ_RUB` | `Input/NorthEnglandctDNA100.csv` and the ctDNA messages generated from it |
| Dr Ada FICTITIOUS | Local (iGene user) | `ZZ_ADA` | `Input/NorthEnglandctDNA100.csv` and the ctDNA messages generated from it |
| Dr Lena FICTITIOUS | Local (iGene user) | `ZZ_LEN` | `Input/NorthEnglandctDNA100.csv` and the ctDNA messages generated from it |
| Dr Pia FICTITIOUS | Local (iGene user) | `ZZ_PIA` | `Input/EDITestPatientsctDNA.csv` |
| Dr Dov FICTITIOUS | Local (iGene user) | `ZZ_DOV` | `Input/EDITestPatientsctDNA.csv` |
| Dr Mira FICTITIOUS | Local (iGene user) | `ZZ_MIR` | `Input/EDITestPatientsctDNA.csv` |
| Dr Bernard FICTITIOUS | GMC | `C9000102` | `Input/V2/R01/Clatterbridge-REN-ORU_R01.txt`, `Input/V2/R01/LUFT_ORU_For_Clatterbridge.txt` (PV1-7, PV1-8, ORC-12, OBR-16, OBR-32); `Input/OmicsDSSOrderDataExport.csv`; notebook 01 |
| Dr Alice FICTITIOUS | GMC | `C9000101` | `Input/V2/O01/histotrac-MFT-chimerism.txt` (PV1-7, ORC-12, OBR-16) |
| Dr Wilfred FICTITIOUS | GMC | `C9000107` | `Input/V2/O01/Clatterbridge-Order.txt` and the CCC examples (PV1-7, ORC-12, OBR-16) |
| Dr Tobias FICTITIOUS | GMC | `C9000108` | `Input/V2/O21/OML_O21_REN_Chimerism.txt` (PV1-7) |
| Dr Magnus FICTITIOUS | Local (Clatterbridge) | `CCCL901` | `Input/V2/O21/OML_O21_REN_Chimerism.txt` and the CCC examples (ORC-12, OBR-16) |
| Dr Hugo FICTITIOUS | GMC | `C9000109` | `Input/V2/O01/EPICJune26.txt` (ORC-12) |
| FICTITIOUS, Greta | Local (placeholder) | `999` | `Input/V2/O01/EPIC-Faulty.txt`, `Input/V2/O01/Fetus-LRI-Variant-2-O01.txt`, `Input/FHIR/**/Bundle-748683741.json` |
| Gideon FICTITIOUS | None | - | `Input/V2/R01/igene-hods.txt` (OBR-32) |
| Rowan FICTITIOUS | None | - | `Input/V2/R01/ctDNA-Glasgow.txt` (OBR-32) |
| Finn FICTITIOUS | None | - | `Input/V2/R01/ORU_R01_DLIMS.txt`, `Input/V2/O51iGene/igene-o51-1.txt` (OBR-32) |
| Jude FICTITIOUS | Local (iGene user) | `Jude.FICTITIOUS` | `Input/V2/O51iGene/igene-o51-2.txt` (OBR-32) |
| Dr C A FICTITIOUS | None | - | `Input/V2/R01/WALES_ORU_R01_TX.txt` (OBR-16) |
| Dr Nadia FICTITIOUS | Local | `GE.FICNAD` | `Input/FHIR/**/LiverpoolWomens-1.json`, `Input/FHIR/O21/Liverpool_O21_Apr26.json`; email `nadia.fictitious@example.nhs.uk` |
| kira fictitious | None | - | `Input/ASTM/R32/cepheid-*.txt` (Cepheid BCR-ABL results) and the implementation guide's `Observation-BCRABL-*.json` (`performer.display`) |
| Peregrine FICTITIOUS | None (email only) | `peregrine.fictitious@example.nhs.uk` | Report-recipient email answers in `Input/V2/O01/EPICJune9.txt`, `Input/V2/O01/ORM_O01_R0A.txt` and `Input/FHIR/**/Bundle-748683741.json` |
| Rafe FICTITIOUS | None (email only) | `Rafe.Fictitious@example.nhs.uk` | `Input/FHIR/O21/LiverpoolWomens-1.json` (`telecom`) |
| Rhoda FICTITIOUS | None (email only) | `rhoda.fictitious@example.nhs.uk` | Referring clinician email answers in `Input/FHIR/O21/Liverpool_O21_Apr26.json` |
{:.grid}

Codes that came with placeholder names (`surname^forename`) were replaced on their own: GMC `C9000110`, `C9000111`, `C9000112`, GP `G9000103` and NMC `99Z9901E`, in `Input/V2/O01/histotrac-MFT-HLA.txt`, `Input/V2/R01/histotrac-MFT.txt` and `Input/FHIR/**/LiverpoolWomens-1.json`.

## OmicsDSS order export

`Input/OmicsDSSOrderDataExport.csv` is a copy of a live export. Its `OrderingProviderIdentifier` and `OrderingProviderName` columns now hold these fictitious ordering providers, one for each distinct provider in the live export. Identifiers keep the live export's shape (`<given>_<family>_<number>`, a bare number, or `<given>_<family>`). `UNK` / `Unknown Unknown` is kept as exported.

| Ordering Provider Name | Ordering Provider Identifier | Requesting Organisation(s) |
|---|---|---|
| Bea FICTITIOUS | `Bea_FICTITIOUS_9000201` | `RBT` |
| Bryn FICTITIOUS | `Bryn_FICTITIOUS_9000227` | `RJN` |
| Dr Abel FICTITIOUS | `9000200` | `RXL` |
| Dr Aldo FICTITIOUS | `Aldo_FICTITIOUS_9000251` | `R0A` |
| Dr Arlo FICTITIOUS | `Arlo_FICTITIOUS_9000226` | `RRF` |
| Dr Bernard FICTITIOUS | `C9000102` | `REN` |
| Dr Cyrus FICTITIOUS | `Cyrus_FICTITIOUS_9000202` | `RXR` |
| Dr Dex FICTITIOUS | `Dex_FICTITIOUS_9000229` | `R0A` |
| Dr Esme FICTITIOUS | `Esme_FICTITIOUS_9000230` | `R0A` |
| Dr Fern FICTITIOUS | `Fern_FICTITIOUS_9000205` | `REN` |
| Dr Greer FICTITIOUS | `Greer_FICTITIOUS_9000232` | `RQ6` |
| Dr Gus FICTITIOUS | `Gus_FICTITIOUS_9000206` | `RBV` |
| Dr Hal FICTITIOUS | `Hal_FICTITIOUS_9000233` | `RBV` |
| Dr Hana FICTITIOUS | `Hana_FICTITIOUS_9000207` | `RXN` |
| Dr Ivo FICTITIOUS | `Ivo_FICTITIOUS_9000208` | `RWW` |
| Dr Jada FICTITIOUS | `Jada_FICTITIOUS_9000209` | `RBL` |
| Dr Jory FICTITIOUS | `Jory_FICTITIOUS_9000235` | `RX1` |
| Dr Kaia FICTITIOUS | `Kaia_FICTITIOUS` | `RBV` |
| Dr Lark FICTITIOUS | `Lark_FICTITIOUS_9000211` | `RBV` |
| Dr Lev FICTITIOUS | `Lev_FICTITIOUS_9000237` | `RM3` |
| Dr Milo FICTITIOUS | `Milo_FICTITIOUS_9000212` | `RBL` |
| Dr Nico FICTITIOUS | `Nico_FICTITIOUS_9000239` | `REN` |
| Dr Nora FICTITIOUS | `Nora_FICTITIOUS_9000213` | `R0A` |
| Dr Otto FICTITIOUS | `Otto_FICTITIOUS_9000214` | `REN` |
| Dr Pax FICTITIOUS | `Pax_FICTITIOUS_9000241` | `R0A` |
| Dr Pearl FICTITIOUS | `Pearl_FICTITIOUS_9000215` | `RBL` |
| Dr Rhea FICTITIOUS | `Rhea_FICTITIOUS_9000242` | `RM3` |
| Dr Saba FICTITIOUS | `Saba_FICTITIOUS_9000218` | `RQ6` |
| Dr Theo FICTITIOUS | `Theo_FICTITIOUS_9000219` | `R0A` |
| Dr Ula FICTITIOUS | `Ula_FICTITIOUS_9000245` | `R0A` |
| Dr Uma FICTITIOUS | `Uma_FICTITIOUS_9000220` | `RBN` |
| Dr Vera FICTITIOUS | `Vera_FICTITIOUS_9000246` | `RQ6` |
| Dr Wade FICTITIOUS | `Wade_FICTITIOUS_9000247` | `RBV` |
| Dr Xavi FICTITIOUS | `Xavi_FICTITIOUS_9000223` | `RBV` |
| Dr Yara FICTITIOUS | `Yara_FICTITIOUS_9000224` | `RBV` |
| Dr Yves FICTITIOUS | `Yves_FICTITIOUS_9000249` | `R0A` |
| Dr Zara FICTITIOUS | `Zara_FICTITIOUS_9000250` | `R0A` |
| Dr Zeno FICTITIOUS | `Zeno_FICTITIOUS_9000225` | `RM3` |
| Fictitious GP | `Generic_Fictitious_GP` | `RBL` |
| Miss Elio FICTITIOUS | `Elio_FICTITIOUS_9000204` | `R0A` |
| Mr Cleo FICTITIOUS | `Cleo_FICTITIOUS_9000228` | `RM3` |
| Mr Dina FICTITIOUS | `Dina_FICTITIOUS_9000203` | `RBN` |
| Mr Flynn FICTITIOUS | `Flynn_FICTITIOUS_9000231` | `RBN` |
| Mr Iris FICTITIOUS | `Iris_FICTITIOUS_9000234` | `REM` |
| Mr Mae FICTITIOUS | `Mae_FICTITIOUS_9000238` | `RBN` |
| Ms Kit FICTITIOUS | `Kit_FICTITIOUS_9000210` | `REP` |
| Professor Quinn FICTITIOUS | `Quinn_FICTITIOUS_9000216` | `RBV` |
| Sol FICTITIOUS | `Sol_FICTITIOUS_9000243` | `R0A` |
| Tove FICTITIOUS | `Tove_FICTITIOUS` | `REP` |
| Unknown Unknown | `UNK` | `UNK` |
| Vito FICTITIOUS | `Vito_FICTITIOUS` | `REP` |
| Wren FICTITIOUS | `Wren_FICTITIOUS_9000222` | `RA7` |
{:.grid}
