# Review: `Clatterbridge-Order.txt` vs NW-GMSA OML_O21 spec

Source: https://nw-gmsa.github.io/en/hl7v2.html#oml_o21-laboratory-order

Message as received (segments split out for readability; file itself must keep `\r`
terminators per repo convention):

```
MSH|^~\&|LAB|CCC||CCC|20260109164121+0000||ORM^O01|27076860.1|P|2.3|||AL|NE|
PID|1||CB0xxxxx15|C2-B20250217143952054|XXX^XXXX^XXX||XXXXXX|M||M|12 XXXX ROAD^HUYTON^LIVERPOOL^MERSEYSIDE^XXX XXXX|||||M||AN0000281729|xxxxxxxxx8652|||||||||||||01|
PV1|1|O|PAL_C863^^^CCC||||C6167060^Wells^Matthew^^^^^^XX|||CLIN HAEM||||||||RCR||NHS|||||||||||||||||||CCC||REG|||202601081200|
ORC|NW|5595441^LAB||090126:RI6||N|^^^^^R||202601091641|
NTE|1||Patient Location 5.Ward 5 TYA|
OBR|1|5595441^LAB||STR^Chimerism (CCC-L)^L|||202601091638||||||||EB|C6167060^Wells^Matthew^^^^^^XX||05094286||||||LAB|||^^^^^R|
OBR|2|5595441^LAB||CD348^Lymph Sub (CD3/4/8/45) (CCC-L)^L|||202601091638||||||||S|C6167060^Wells^Matthew^^^^^^XX||05094286||||||LAB|||^^^^^R|
```

## 1. Message type — MSH-9 / MSH-12 (critical)

- **Current:** `MSH-9 = ORM^O01`, `MSH-12 = 2.3`
- **Spec:** MSH-9 must be `OML^O21^OML_O21`; MSH-12 must be `2.5.1`
- **Why it matters:** `ORM^O01` isn't the message this repo's transform pipeline / IG target
  (`OML_O21`) is built for. The file lives in `Input/V2/O01/`, but the target spec page is
  the O21 laboratory order — these are two different trigger events with different
  segment grammars (O21 nests ORC/OBR/OBX/SPM under a repeating ORDER group; O01 doesn't).
  Confirm intent: if this message is meant to exercise the OML_O21 profile, it needs
  re-issuing as an actual `OML^O21^OML_O21` message, not just a header rename.

## 2. MSH-4 Sending Facility

- **Current:** `CCC` (bare string)
- **Spec:** HD type, ODS code required
- **Suggested:** `CCC^<ODS code>^ODS` (populate the actual ODS site code for Clatterbridge).

## 3. PID-3 Patient Identifier List — no NHS Number, no CX typing

- **Current:** `CB0xxxxx15` and `C2-B20250217143952054` (PID-3/PID-4), both bare strings
  with no assigning authority / identifier type component.
- **Spec:** PID-3 (CX type) must support NHS Number and Medical Record Number, i.e.
  repeats like `<value>^^^<assigning authority>^<identifier type code>` (e.g.
  `9999999468^^^NHS^NH` for NHS Number, `CB0xxxxx15^^^CCC^MR` for local MRN).
- **Current gap:** no NHS Number appears anywhere in PID-3/4 — `AN0000281729` sits in
  PID-18 (Patient Account Number) and `xxxxxxxxx8652` in PID-19 (SSN Number Patient),
  neither of which is where an NHS Number belongs, and neither is typed as one.
- **Suggested:** move/add the NHS Number into PID-3 as a repeat with `NH` identifier
  type, keep the local CCC MRN as a second PID-3 repeat with `MR`, and only use
  PID-18/19 for their literal defined meaning (account number / SSN) if actually needed.

## 4. ORC — missing Ordering Provider / Ordering Facility, one ORC for two OBRs

- **Current:** single `ORC|NW|5595441^LAB||090126:RI6||N|^^^^^R||202601091641|` precedes
  both OBR segments.
- **ORC-12 (Ordering Provider, XCN):** empty. Spec marks this required/suggested. The
  ordering clinician (`C6167060^Wells^Matthew^^^^^^XX`) is only present down in
  OBR-16, not ORC-12.
- **ORC-21 (Ordering Facility Name, XON):** empty. Spec marks this required/suggested.
- **Structure:** the OML_O21 grammar is `ORDER := ORC, OBSERVATION_REQUEST(1..*){OBR,
  NTE, DG1, OBSERVATION{OBX}, SPECIMEN{SPM}}` — each `ORDER` repeat needs its own ORC.
  Reusing one ORC across two OBRs (even with matching placer number `5595441^LAB`) is
  not valid O21 structure; this needs two ORC/OBR order groups (or confirmation both
  tests genuinely share one order/placer number, in which case each still needs its own
  ORC repeat under O21).

## 5. OBR-6 Requested Date/Time is empty — date landed in the wrong field

- **Current:** field 6 (Requested Date/Time) of both OBR segments is empty; the
  timestamp `202601091638` is instead sitting in field 7 (Observation Date/Time).
- **Spec:** OBR-6 Requested Date/Time is required for OML_O21.
- **Suggested:** populate OBR-6 with the request date/time; only put an actual
  observation/collection date/time in OBR-7 if that's genuinely known and distinct.

## 6. OBR-4 Universal Service Identifier — local codes, not Genomic Test Directory

- **Current:** `STR^Chimerism (CCC-L)^L` and `CD348^Lymph Sub (CD3/4/8/45) (CCC-L)^L`
  — local lab codes (`L` coding system).
- **Spec:** OBR-4 should use the "Genomic Test Directory" value set.
- **Suggested:** either map these to the equivalent Genomic Test Directory code (if
  chimerism/lymphocyte subset testing has a directory entry) and send that as the
  primary triplet with the local code as an alternate (OBR-4.4-4.6), or confirm with
  the IG maintainers that local-only codes are acceptable for this non-genomic test
  type — as-is it won't satisfy the value set binding.

## 7. OBR-31 Reason for Study — missing

- **Current:** empty (field not populated in either OBR).
- **Spec:** CWE type, uses Genomic Clinical Indication Codes.
- **Suggested:** populate with the clinical indication for the test (even if it maps to
  a "non-genomic" or free-text fallback code), since the field is expected on the O21
  profile.

## 8. Missing SPM (Specimen) segment entirely

- **Current:** no SPM segment anywhere in the message.
- **Spec:** SPECIMEN group (SPM, 0..1, conditional — required for a complete order) is
  expected, carrying SPM-4 Specimen Type (SNOMED CT preferred), SPM-8 Specimen Source
  Site, and SPM-30 Accession ID.
- **Suggested:** add an SPM segment per order carrying specimen type (e.g. blood/bone
  marrow, whichever applies to chimerism/lymphocyte subset testing) and the accession
  number `05094286` currently only visible buried in OBR field 18.

## 9. PV1-19 Visit Number — empty

- **Current:** PV1 segment is present but field 19 (Visit Number / Hospital Provider
  Spell Identifier) is blank.
- **Spec:** PV1 is 0..1 and only expected "if PV1-19 known" — since the segment is
  being sent anyway, populate PV1-19 or drop the segment if the spell ID genuinely
  isn't known.

## Summary — priority order

1. **Message type**: confirm whether this should actually be `OML^O21^OML_O21`
   (v2.5.1) rather than `ORM^O01` (v2.3) — everything else in the spec assumes O21
   structure.
2. **PID-3**: add a properly-typed NHS Number CX repeat.
3. **ORC-12 / ORC-21**: populate ordering provider and ordering facility; split into
   one ORC per OBR order group.
4. **OBR-6**: move the request timestamp out of OBR-7 into OBR-6.
5. **SPM**: add specimen segment(s) with type, source site, accession ID.
6. **OBR-31**: populate Reason for Study.
7. **OBR-4**: review coding against the Genomic Test Directory value set.
8. **MSH-4 / PV1-19**: minor — populate ODS code and spell ID if available.