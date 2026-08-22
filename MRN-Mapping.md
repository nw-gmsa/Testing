# Master List: NHS Number / Surname -> Trust MRN

Cross-referenced from every patient identifier found in `Input/StarLIMSSampleData.csv`, `Input/NorthEnglandctDNA100.csv`, `Input/EDITestPatientsctDNA.csv`, `Input/NEYctDNA.csv`, `Input/V2/**/*.txt` (PID-2/PID-3), and `Input/FHIR/**/*.json` (`Patient.identifier`), grouped by NHS number. One column per assigning organisation/trust code seen in the source data; a blank cell means that patient has no MRN recorded for that trust in the current fixtures. `Patient Number(s)` lists every `PatientAccessionIdentifier` seen for that NHS number across the StarLIMS/ctDNA CSVs (a patient can have more than one, one per order). `Mothers Patient Number` is only populated for fetus/baby rows (see below) and gives the `PatientAccessionIdentifier` of the mother's own row.

**Caveats:**
- `EPI` is not an ODS trust code — it's the assigning-authority tag some EPIC-sourced test files (`EPIC-*.txt`, `Fetus-LRI-Variant-2-O01.txt`) use in place of a real trust code.
- `1234567` recurs as an MRN for several unrelated patients under `R0A` — it's a placeholder value reused across multiple hand-crafted test files, not a real per-patient identifier.
- Where a patient shows more than one MRN in the same trust column (semicolon-separated), the source files disagree — see the file list below the table.
- `Input/EDITestPatientsctDNA.csv` and `Input/NEYctDNA.csv` MRNs are not read directly into the trust columns — their data is already captured via the `ctdna*.txt`/`ctdna9999999*.txt` HL7 v2 files they generate; they're only used here for `Patient Number(s)`.
- Fetus/baby rows in `Input/StarLIMSSampleData.csv` (`PatientGivenName` of the form `Fetus of <mother>`/`Baby of <mother>`) have no NHS number, DOB, or sex of their own — a fetus/baby isn't PDS-registered, so those fields are blank rather than the mother's. They keep the mother's postcode (specimen ships from her address) but get their own hospital MRN and `PatientAccessionIdentifier`, distinct from the mother's; the CSV's `MotherPatientAccessionIdentifier` column, mirrored here as `Mothers Patient Number`, links back to the mother's own `PatientAccessionIdentifier`/row. Because they have no NHS number, they can't be folded into the mother's NHS-number-keyed table row below — each gets its own row with a blank NHS Number cell instead, placed directly under the mother's row.

| NHS Number | Surname | Patient Number(s) | Mothers Patient Number | 01A | EPI | QE1 | R0A | R0B | RAE | RBS | RBT | RCB | RCD | REM | REP | RHQ | RJE | RJR | RK5 | RM3 | RMC | RMP | RNN | RPY | RQM | RR8 | RTD | RTG | RTR | RTX | RVR | RWA | RWJ | RX1 | RXK | RXL | RXP | RXR | RXW | UNK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 756 977 3373 | Appclindoc |  |  |  | 20003025 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3249 | Birmingham | 345574 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1234567 | AB21580 |  |  |  |  |
| 973 738 3370 | Blackburn | 200004 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RXR6078306 |  | ICE212730 |
| 973 738 3273 | Bolton | 200026 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1234567 | RMC7021955 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | AG30913 |  |  |  |  |
| 973 787 3882 | Bradford | 200009 |  |  |  |  |  |  | RAE9191583 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3362 | Brough | 200003 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RNN1799141 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 6016117 |  |  |
|  | Brough (Baby of Gilly) | 200081 | 200003 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RXR200081 |  |  |
| 973 738 3389 | Burnley | 200008 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | B6789567; RXR5797566 |  | 7345828 |
| 973 738 3338 | Buxton | 200024 |  |  |  | RXR3097000 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RWJ7613989 |  |  |  |  |  |  |  |
|  | Buxton (Baby of Lysa) | 200083 | 200024 |  |  | QE1200083 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 944 930 5552 | Chislett | 200067 |  |  |  |  | G179494 |  |  |  |  |  |  |  |  | RHQ4697183 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3281 | Congleton | 200031 |  |  |  |  | ABC14567 |  |  |  | RBT5094163 |  |  |  | W0007939 |  |  | 1571313 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 787 3998 | Durham | 200029 |  |  |  |  |  |  | 336577 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RXP7136968 |  |  |  |
| 999 999 9476 | Editestpatient | 300000 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTG1565235 |  |  |  |  |  |  |  |  |  |  |  |  |
| 999 999 9565 | Editestpatient | 300001 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RQM1552395 |  |  |  |  |  |  |  |  | RX14614942 |  |  |  |  |  |  |
| 999 999 9506 | Editestpatient | 300002 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RK53341875 |  |  |  |  |  |  |  |  |  |  |  | RVR1065281 |  |  |  |  |  |  |  |  |  |
| 999 999 9603 | Editestpatient | 300003 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RK59690678 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RX14389121 |  |  |  |  |  |  |
| 999 999 9522 | Editestpatient | 300004 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RPY1365182 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RXW5005259 |  |
| 999 999 9557 | Editestpatient | 300005 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RXW5420830 |  |
| 999 999 9484 | Editestpatient | 300007 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RPY9047131 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RXW4460305 |  |
| 999 999 9573 | Editestpatient | 300009 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RK57213042 |  |  |  |  | RPY2286785 |  |  |  |  |  |  |  |  |  | RX17825652 |  |  |  |  |  |  |
| 999 999 9581 | Editestpatient | 300010 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RK57256476 |  |  |  |  |  |  |  |  |  |  |  | RVR6796096 |  |  |  |  |  |  |  |  |  |
| 999 999 9514 | Editestpatient | 300011 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RJE8170665 |  |  |  |  |  |  | RPY8254161 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 999 999 9468 | Editestpatient | 300015 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTG9688587 |  |  | RVR5177394 |  |  |  |  |  |  |  |  |  |
| 999 999 9549 | Editestpatient | 300021 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTG7042851 |  |  |  |  |  | RX17717436 |  |  |  |  | RXW3271523 |  |
| 999 999 9530 | Editestpatient | 300022 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RPY3798123 | RQM7318513 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 999 999 9492 | Editestpatient | 300024 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RJE6068695 |  |  |  |  |  |  | RPY5120065 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 999 999 9900 | Gp Comms,\R\'#$% |  |  |  | 207230 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3346 | Hawes | 200018 |  |  |  |  |  |  |  | B67890 |  |  | RCD9077482 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 6009355 |  |  |
| 973 787 3963 | Hull | 200048 |  |  |  |  |  |  |  |  |  |  |  |  |  | WL3847 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RWA4931899 |  |  |  |  |  |  |  | RMP00416845 |
|  | Hull (Fetus of Yara) | 200082 | 200048 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | UNK200082 |
| 590 011 1075 | Jones |  |  |  | 20006087 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3354 | Kendal | 200063 |  |  |  |  | 10991888 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTX3170820 |  |  |  |  |  |  |  |  |  |  |
| 973 738 3214 | Lancaster | 200006 |  |  |  |  | 2401711 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTX7565482 |  |  |  |  |  |  |  |  |  |  |
| 973 738 3222 | Leeds | 32737 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | L765432; RR83108802; RXR0817610 |  |  |  |  |  |  |  |  |  |  |  |  |  | 79463383 |
| 973 738 3206 | Liverpool | 200021 |  |  |  |  | 9041393 |  |  |  |  |  |  | REM7442130 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3230 | London | 345654 |  |  |  |  | 505181 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1234567 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | London (Fetus of Cersei) | 200080 | 345654 |  |  |  | R0A200080 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3192 | Manchester | 200000 |  |  |  |  | 1234567; R0A4990415 |  |  | A12345 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTX0641579 |  |  |  |  |  |  |  |  |  |  |
| 973 787 3971 | Middlesborough | 200001 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1342615; RTR2920101 |  |  |  |  |  |  |  |  |  |  |  |
| 973 787 3947 | Newcastle | 200041 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTD9944958; RXR3178922 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3311 | Northwich | 200013 |  |  |  |  |  |  |  |  | RBT1044193 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RXR3669592 |
| 973 738 3265 | Nottingham | 200034 |  |  |  |  |  |  |  |  |  | RCB2009594 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1234567 |  |  |  |  |  |  |
| 973 787 3858 | Sheffield | 200012 |  |  |  |  |  |  |  |  |  |  |  |  |  | RHQ5948241; RXR3302855 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 2069650 |
| 973 738 3413 | Streford | 200007 |  |  |  |  | R0A3594349 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 787 3874 | Sunderland | 200058 |  |  |  |  |  | R0B2364016 |  |  |  |  |  |  |  |  |  |  |  |  | RMC00177314 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3397 | Tameside | 200016 |  |  |  |  | B6789012 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RMP6419544 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 3746334 |
| 590 012 3170 | Testbeaker |  |  |  | 20010652 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3303 | Warrington | 345660 |  | RXR0303179 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3257 | Wrexham | 200028 |  |  |  |  | 3617899 |  |  |  |  |  |  | REM7676150 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 787 3866 | York | 336384 |  |  |  |  |  |  |  |  |  | 658357 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

## Trust code legend

| Code | Name |
|---|---|
| 01A | NHS East Lancashire CCG |
| EPI | _unknown_ |
| QE1 | NHS Lancashire and South Cumbria Integrated Care Board |
| R0A | Manchester University NHS Foundation Trust |
| R0B | South Tyneside and Sunderland NHS Foundation Trust |
| RAE | Bradford Teaching Hospitals NHS Foundation Trust |
| RBS | _unknown_ |
| RBT | Mid Cheshire Hospitals NHS Foundation Trust |
| RCB | York and Scarborough Teaching Hospitals NHS Foundation Trust |
| RCD | Harrogate and District NHS Foundation Trust |
| REM | Liverpool University Hospitals NHS Foundation Trust |
| REP | Liverpool Women's Hospital |
| RHQ | Sheffield Teaching Hospitals NHS Foundation Trust |
| RJE | University Hospitals of North Midlands NHS Trust |
| RJR | Countess of Chester Hospital NHS Foundation Trust |
| RK5 | Sherwood Forest Hospitals NHS Foundation Trust |
| RM3 | _unknown_ |
| RMC | Bolton NHS Foundation Trust |
| RMP | Tameside & Glossop Integrated Care NHS Foundation Trust |
| RNN | North Cumbria Integrated Care NHS Foundation Trust |
| RPY | The Royal Marsden NHS Foundation Trust |
| RQM | Chelsea and Westminster Hospital NHS Foundation Trust |
| RR8 | Leeds Teaching Hospitals NHS Trust |
| RTD | The Newcastle upon Tyne Hospitals NHS Foundation Trust |
| RTG | University Hospitals of Derby and Burton NHS Foundation Trust |
| RTR | South Tees Hospitals NHS Foundation Trust |
| RTX | University Hospitals of Morecambe Bay NHS Foundation Trust |
| RVR | Epsom and St Helier University Hospitals NHS Trust |
| RWA | Hull University Teaching Hospitals NHS Trust |
| RWJ | Stockport NHS Foundation Trust |
| RX1 | Nottingham University Hospitals NHS Trust |
| RXK | _unknown_ |
| RXL | Blackpool Teaching Hospitals NHS Foundation Trust |
| RXP | County Durham and Darlington NHS Foundation Trust |
| RXR | East Lancashire Hospitals NHS Trust |
| RXW | The Shrewsbury and Telford Hospital NHS Trust |
| UNK | _unknown_ |
