# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repo generates and validates HL7 v2 / FHIR test examples that conform to the
**North West Genomic Medicine Service Alliance (NW-GMSA) FHIR Implementation Guide**:
https://nw-gmsa.github.io/en/

It is not an application — it is a collection of Jupyter notebooks and generated/received
test data used to exercise an HL7 v2 <-> FHIR transformation engine and an interface
engine (RIE), and to validate the resulting FHIR against the IG.

## Environment setup

- Python 3.12 virtualenv (`.venv`), scispacy-compatible.
- Install deps: `pip install -r requirements.txt`
- Additional required installs (not in requirements.txt):
  - `python -m spacy download en_core_web_sm`
  - `pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz`
- Secrets/config live in `.env` (gitignored) and are loaded via `python-dotenv` in
  notebooks: `V2_SERVER`, `V2_TOOLS`, `FHIR_SERVER`, `OAUTH2_TOKEN`, `CLIENT_ID`,
  `CLIENT_SECRET`.
- macOS WeasyPrint fix: `export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_FALLBACK_LIBRARY_PATH`

## Architecture / data flow

There is no application code to build — work happens by running notebook cells against
a locally-networked transformation/interface stack (typically at `192.168.1.x`):

- **`V2_TOOLS`** server exposes `/transformToFHIR` and `/transformToV2` endpoints that
  convert between raw HL7 v2 (ER7) messages and FHIR bundles.
- **`V2_SERVER`** (interface engine / RIE) accepts raw HL7 v2 messages posted directly
  to its root, simulating a real feed into the trust's systems.
- **`FHIR_SERVER`** (FHIR data repository / CDR) is where converted FHIR bundles are
  ultimately persisted, using OAuth2 client-credentials (`OAUTH2_TOKEN`, `CLIENT_ID`,
  `CLIENT_SECRET`) or, in older notebooks, HTTP Basic auth.

Typical round-trip exercised by `Testing.ipynb` per message type (O21/O01 orders, R01
reports, ctDNA reports):
1. Read a raw HL7 v2 `.txt` file from `Input/V2/<messageType>/`.
2. POST to `toolsServer/transformToFHIR` -> save FHIR bundle to `Output/FHIR/<type>/`.
3. POST the FHIR bundle to the FHIR server / RIE.
4. POST back through `toolsServer/transformToV2` -> save round-tripped v2 to
   `Output/V2/<type>/` for diff/comparison against the original.

**FHIR IG validation** (`FHIR Validation.ipynb`) runs the HL7 FHIR validator CLI
(`validator_cli.jar`, downloaded from the hapifhir releases) against output bundles
using the packaged IG (`package.tgz`), e.g.:
```
java -jar validator_cli.jar Output/FHIR/R01/<file>.json -version 4.0.1 -ig package.tgz \
  -bundle DiagnosticReport:0 https://fhir.nwgenomics.nhs.uk/StructureDefinition/DiagnosticReport...
```
Results (OperationOutcome JSON) land in `Results/FHIR/<type>/` and are summarized into
pandas DataFrames / HTML reports (`Results/report_template.html`).

**Report rendering pipeline** (`miscellaneous-notebooks/MarkdownToPDF.ipynb`,
`miscellaneous-notebooks/PDFExtractionFromFHIRandMarkdownFromPDF.ipynb`, `miscellaneous-notebooks/PDFMetadataExtraction.ipynb`,
`miscellaneous-notebooks/PDFTextAnalytics.ipynb`): extracts embedded PDFs/Binary resources from FHIR
DiagnosticReports, converts markdown lab narratives to PDF via WeasyPrint, and back
again via `pymupdf`/`pymupdf4llm`/`tabula`/`pypdf`, with optional spaCy/scispacy NLP
over the extracted text.

**Bulk generation** (`miscellaneous-notebooks/SendctDNAReports.ipynb`, `miscellaneous-notebooks/NEYctDNA-HL7v2ORU_R01.ipynb`,
`miscellaneous-notebooks/CSVTools.ipynb`): builds large batches of synthetic ctDNA HL7 v2 R01 messages from CSV
patient/order data (`Input/PDS/*.csv`, `NotGit/*SampleData.csv`) and posts them to
`V2_SERVER` in bulk (see `Input/V2/R01/ctdna<NHSNumber>_<seq>.txt` naming convention;
`9999999*` prefix = NHS England EDI test patients).

**VCF -> FHIR genomics-reporting `variant`** (`miscellaneous-notebooks/VCFToFHIRVariant.ipynb`): standalone
demo, unrelated to the NW-GMSA v2/FHIR round-trip above. Parses a VCF from `Input/VCF/`
(field-to-LOINC mapping is read directly out of the VCF's own `##INFO`/`##FORMAT`
`Description` meta-lines) and builds `Observation` resources conforming to the **HL7
international Genomics Reporting IG** `variant` profile
(`http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/variant`,
https://build.fhir.org/ig/HL7/genomics-reporting/StructureDefinition-variant.html) — a
different IG from NW-GMSA. Component LOINC codes/value shapes were verified against the
IG's own published examples (`Observation-VariantExample2`, `-ExampleGermlineDEL`,
`-ExampleGermlineCNV`, etc.) rather than assumed; where no confirmed LOINC *answer* code
exists, components fall back to text-only `CodeableConcept`s. Output goes to
`Output/FHIR/GenomicsReporting/`, and validates against the real published package
`hl7.fhir.uv.genomics-reporting#3.0.0` (not the vendored NW-GMSA `package.tgz`), with
results in `Results/FHIR/GenomicsReporting/`.

## Directory layout

- `Input/V2/{O01,O21,R01}` — hand-crafted/generated source HL7 v2 test messages, keyed
  by trigger event.
- `Input/FHIR/` — source FHIR examples used for `transformToV2`.
- `Input/PDS/`, `Input/ctDNA/`, `Input/ASTM/` — reference patient data (PDS extracts) and
  other source formats (ASTM instrument output).
- `Input/VCF/` — source VCF files for the standalone `miscellaneous-notebooks/VCFToFHIRVariant.ipynb` demo (HL7
  genomics-reporting IG `variant` profile, not the NW-GMSA pipeline).
- `Output/{FHIR,V2,PDF,Markdown}/<type>/` — generated artifacts from the transform/render
  pipelines (`<type>` includes `GenomicsReporting` for the VCF demo's output).
- `Results/FHIR/<type>/` — FHIR validator OperationOutcomes and generated HTML reports.
- `NotGit/` — real/sensitive sample data (gitignored), never committed.
- `Shire.md` — trust-specific (MFT) notebook command notes, same pattern as README.md.
- `package.tgz` / `validator_cli.jar` — vendored IG package and FHIR validator (gitignored, regenerated by `FHIR Validation.ipynb`).

## Conventions

- HL7 v2 test files **must** use CR or CRLF line endings, not bare LF — the v2 parser
  requires segment terminators, and the interface engine expects `\r`.
- Test examples are based on the NW Genomics test patients and NHS England PDS
  integration-environment test patients (see README.md links) — keep new synthetic
  patients consistent with those sources rather than inventing new NHS numbers ad hoc.
- When a new HL7 v2 or FHIR example needs a hospital MRN for a given NHS trust, reuse
  the MRN recorded for that NHS number/trust pair in `MRN-Mapping.md` (a master list
  cross-referenced from `Input/StarLIMSSampleData.csv`, `Input/V2/**`, and
  `Input/FHIR/**`) rather than inventing a new one — keeps a trust's MRN consistent for
  the same patient across all test fixtures. Regenerate/update that file when new
  examples introduce a patient/trust pair it doesn't yet cover.
- Server endpoints (`192.168.1.x`) are local/lab infrastructure, not committed as
  constants — always read them from `.env` via `load_dotenv()`, matching existing
  notebook cells.
- `IntegrationTest.py`'s `TEST_GROUPS["dwgs"]` fixture list must track
  `notebooks/08-subcontracted-laboratory-order-from-external-glh.ipynb`'s worked
  example: if that notebook starts building the order from a different `dWGS.csv` row
  (or an additional one), its `order_filename` (`f"dWGS_{row['referral_id']}.json"`)
  changes/grows too, and `Input/FHIR/O21/`'s corresponding file(s) must be added to that
  group's `"O21"` case list (or replace the current one) so the script's coverage
  doesn't silently drift from what the notebook actually exercises.
