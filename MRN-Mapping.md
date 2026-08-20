# Master List: NHS Number / Surname -> Trust MRN

Cross-referenced from every patient identifier found in `Input/StarLIMSSampleData.csv`, `Input/V2/**/*.txt` (PID-2/PID-3), and `Input/FHIR/**/*.json` (`Patient.identifier`), grouped by NHS number. One column per assigning organisation/trust code seen in the source data; a blank cell means that patient has no MRN recorded for that trust in the current fixtures.

**Caveats:**
- `EPI` is not an ODS trust code — it's the assigning-authority tag some EPIC-sourced test files (`EPIC-*.txt`, `Fetus-LRI-Variant-2-O01.txt`) use in place of a real trust code.
- `1234567` recurs as an MRN for several unrelated patients under `R0A` — it's a placeholder value reused across multiple hand-crafted test files, not a real per-patient identifier.
- Where a patient shows more than one MRN in the same trust column (semicolon-separated), the source files disagree — see the file list below the table.

| NHS Number | Surname | 01A | 7A4 | EPI | QE1 | R0A | RAE | RBS | RCB | REP | RHQ | RJE | RJR | RK5 | RM3 | RMC | RPY | RQM | RR8 | RTD | RTG | RTR | RTX | RVR | RX1 | RXK | RXL | RXR | RXW | UNK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 756 977 3373 | Appclindoc |  |  | 20003025 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3249 | Birmingham |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1234567 | AB21580 |  |  |  |
| 973 738 3370 | Blackburn |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | ICE212730 |
| 973 738 3273 | Bolton |  |  |  |  |  |  |  |  |  |  |  |  |  | 1234567 |  |  |  |  |  |  |  |  |  |  |  | AG30913 |  |  |  |
| 973 787 3882 | Bradford |  |  |  |  |  | RAE9191583 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3362 | Brough |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 6016117 |  |  |
| 973 738 3389 | Burnley |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | B6789567 |  | 7345828 |
| 973 738 3338 | Buxton |  |  |  | RXR3097000 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 944 930 5552 | Chislett |  |  |  |  | G179494 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3281 | Congleton |  |  |  |  | ABC14567 |  |  |  | W0007939 |  |  | 1571313 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 787 3998 | Durham |  |  |  |  |  | 336577 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 999 999 9468 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTG9688587 |  |  | RVR5177394 |  |  |  |  |  |  |
| 999 999 9476 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTG1565235 |  |  |  |  |  |  |  |  |  |
| 999 999 9484 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RPY9047131 |  |  |  |  |  |  |  |  |  |  |  | RXW4460305 |  |
| 999 999 9492 | Editestpatient |  |  |  |  |  |  |  |  |  |  | RJE6068695 |  |  |  |  | RPY5120065 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 999 999 9506 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  | RK53341875 |  |  |  |  |  |  |  |  |  | RVR1065281 |  |  |  |  |  |  |
| 999 999 9514 | Editestpatient |  |  |  |  |  |  |  |  |  |  | RJE8170665 |  |  |  |  | RPY8254161 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 999 999 9522 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RPY1365182 |  |  |  |  |  |  |  |  |  |  |  | RXW5005259 |  |
| 999 999 9530 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RPY3798123 | RQM7318513 |  |  |  |  |  |  |  |  |  |  |  |  |
| 999 999 9549 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTG7042851 |  |  |  | RX17717436 |  |  |  | RXW3271523 |  |
| 999 999 9557 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RXW5420830 |  |
| 999 999 9565 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RQM1552395 |  |  |  |  |  |  | RX14614942 |  |  |  |  |  |
| 999 999 9573 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  | RK57213042 |  |  | RPY2286785 |  |  |  |  |  |  |  | RX17825652 |  |  |  |  |  |
| 999 999 9581 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  | RK57256476 |  |  |  |  |  |  |  |  |  | RVR6796096 |  |  |  |  |  |  |
| 999 999 9603 | Editestpatient |  |  |  |  |  |  |  |  |  |  |  |  | RK59690678 |  |  |  |  |  |  |  |  |  |  | RX14389121 |  |  |  |  |  |
| 999 999 9900 | Gp Comms,\R\'#$% |  |  | 207230 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3346 | Hawes |  |  |  |  |  |  | B67890 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 6009355 |  |  |
| 973 787 3963 | Hull |  |  |  |  |  |  |  |  |  | WL3847 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RMP00416845 |
| 590 011 1075 | Jones |  |  | 20006087 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3354 | Kendal |  |  |  |  | 10991888 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3214 | Lancaster |  |  |  |  | 2401711 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3222 | Leeds |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | L765432; RR83108802; RXR0817610 |  |  |  |  |  |  |  |  |  |  | 79463383 |
| 973 738 3206 | Liverpool |  |  |  |  | 9041393 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3230 | London |  |  |  |  | 505181 |  |  |  |  |  |  |  |  |  |  | 1234567 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3192 | Manchester |  |  |  |  | 1234567; R0A4990415 |  | A12345 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RTX0641579 |  |  |  |  |  |  |  |
| 973 787 3971 | Middlesborough |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1342615 |  |  |  |  |  |  |  |  |
| 973 787 3947 | Newcastle |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RXR3178922 |  |  |  |  |  |  |  |  |  |  |
| 973 738 3311 | Northwich |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RXR3669592 |
| 973 738 3265 | Nottingham |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1234567 |  |  |  |  |  |
| 973 787 3858 | Sheffield |  |  |  |  |  |  |  |  |  | RXR3302855 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 2069650 |
| 973 787 3874 | Sunderland |  |  |  |  |  |  |  |  |  |  |  |  |  |  | RMC00177314 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3397 | Tameside |  |  |  |  | B6789012 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 3746334 |
| 590 012 3170 | Testbeaker |  |  | 20010652 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3303 | Warrington | RXR0303179 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 738 3257 | Wrexham |  | 403281375 |  |  | 3617899 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 973 787 3866 | York |  |  |  |  |  |  |  | 658357 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

## Trust code legend

| Code | Name |
|---|---|
| 01A | NHS East Lancashire CCG |
| 7A4 | _unknown_ |
| EPI | _unknown_ |
| QE1 | NHS Lancashire and South Cumbria Integrated Care Board |
| R0A | Manchester University NHS Foundation Trust |
| RAE | _unknown_ |
| RBS | _unknown_ |
| RCB | _unknown_ |
| REP | Liverpool Women's Hospital |
| RHQ | _unknown_ |
| RJE | _unknown_ |
| RJR | Countess of Chester Hospital NHS Foundation Trust |
| RK5 | _unknown_ |
| RM3 | _unknown_ |
| RMC | _unknown_ |
| RPY | _unknown_ |
| RQM | _unknown_ |
| RR8 | _unknown_ |
| RTD | _unknown_ |
| RTG | _unknown_ |
| RTR | _unknown_ |
| RTX | University Hospitals of Morecambe Bay NHS Foundation Trust |
| RVR | _unknown_ |
| RX1 | _unknown_ |
| RXK | _unknown_ |
| RXL | Blackpool Teaching Hospitals NHS Foundation Trust |
| RXR | East Lancashire Hospitals NHS Trust |
| RXW | _unknown_ |
| UNK | _unknown_ |
