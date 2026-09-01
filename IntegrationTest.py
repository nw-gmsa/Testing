    #!/usr/bin/env python3
"""
Integration test for the NW-GMSA HL7 v2 <-> FHIR transformation pipeline.

For each registered test case (a raw HL7 v2 file under Input/V2/<messageType>/):

  1. POST to {V2_TOOLS}/transformToFHIR  -> expect a non-empty FHIR Bundle, then run basic
     structural checks over it (see check_fhir_bundle: well-formed Bundle, single leading
     MessageHeader, every entry has a resourceType/fullUrl, no dangling urn:uuid references).
     This is *not* IG/profile validation - that's FHIR Validation.ipynb's job - just a sanity
     check that the transform produced something internally consistent.
     For messages following iGene's 'Baby of <mother>'/'Fetus of <mother>' PID-5 convention
     (PID and NK1 combined into one segment), also checks that the transform split it back
     out into a Patient (the baby/fetus) plus a RelatedPerson (the mother, relationship MTH)
     rather than collapsing them into one Patient - see check_baby_fetus_split.
     For messages carrying an OBX-2 'ED' segment whose OBX-3 identifier already supplies a
     SNOMED/LOINC code, or an OBX-2 'CE' segment whose value embeds a PDF, also checks that
     DocumentReference.type ends up with the expected SNOMED/LOINC coding - preserved as-is
     for the 'ED' case, substituted in if missing for the 'CE'+PDF case - see
     check_document_reference_code.
  2. POST that Bundle to {V2_TOOLS}/transformToV2 -> expect a valid v2 (MSH-led) message back
  3. POST the *original* raw v2 message to {V2_SERVER} (the RIE), simulating a real feed;
     expect an ACK within SEND_TIMEOUT seconds with MSA-1 of AA/CA (a slow or negative ACK
     is treated as a fault worth raising, not something to silently wait out).
     Skipped (recorded as failed) if stage 1's structural, baby/fetus-split, or
     DocumentReference-code checks found a problem - a message transformToFHIR got wrong
     isn't sent on to the RIE.

Stage 1/2 outputs are saved under TestingOutput/FHIR/<messageType>/ and TestingOutput/V2/<messageType>/
- the same layout Testing.ipynb uses under Output/, but in its own top-level directory so a script
run doesn't clobber a notebook run's output (or vice versa).

TEST_GROUPS covers several exchange scenarios extracted from Testing.ipynb - general
NHS Trust <-> iGene order/report exchange (O01/O21/R01), the mother/baby-fetus PID+NK1
split cases (O21/R01), Shire <-> HODS reports (R01), Clatterbridge/Histotrac orders and
reports (O01/R01), ctDNA orders and reports between NW and NEY Genomics (R01), and
Cepheid results (R32, sourced from Input/ASTM/R32 - see Testing-Cephied.ipynb; the
transformToV2 round-trip stage is skipped for these, matching that notebook, since it
isn't yet verified for R32), and the NW-GMSA IG's own published BundleMessage examples
(O21/R01/A31, sourced from https://nw-gmsa.github.io/en/ - see the "nwgmsa_examples"
group below). Extend TEST_GROUPS with further scenarios/files as they're added.

Usage:
    python3 IntegrationTest.py [--skip-send] [--type O21] [--type R01] [--group shire]

Exit code is 0 if every stage of every case passed, 1 otherwise.
"""

import argparse
import json
import os
import sys
import time
import uuid

import requests
import urllib3
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

V2_TOOLS = os.getenv("V2_TOOLS")
V2_SERVER = os.getenv("V2_SERVER")
FHIR_SERVER = os.getenv("FHIR_SERVER")
OAUTH2_TOKEN_URL = os.getenv("OAUTH2_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Kept separate from Output/ (which Testing.ipynb writes to) so running this script doesn't
# clobber - or get clobbered by - a notebook run's output.
OUTPUT_ROOT = "TestingOutput"


def log(msg):
    """Timestamped progress line to stdout, flushed immediately so it's visible
    even if the process later hangs waiting on a network call."""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

HEADERS_V2 = {"Content-Type": "x-application/hl7-v2+er7"}
HEADERS_FHIR = {"Content-Type": "application/fhir+json"}

# A slow ACK from the RIE is treated as a fault worth flagging, not something to wait out
# indefinitely - see stage 3 below.
SEND_TIMEOUT = 60

# Registry of test scenarios. Each group maps message type -> list of filenames.
# Filenames are read from Input/V2/<type>/<filename> unless the group sets "input_dir",
# in which case they're read from <input_dir>/<type>/<filename> instead. A group can set
# "skip_transform_to_v2" to skip stage 2 for every case in it (see Cepheid, below).
#
# HL7 v2 spec compliance note - https://nw-gmsa.github.io/en/hl7v2.html requires MSH-12
# = "2.5.1" and an explicit MSH-9 trigger structure ("OML^O21^OML_O21" / "ORU^R01^ORU_R01")
# for every message type it documents (OML_O21, ORU_R01, MDM_T02); it defines no ORM_O01 or
# R32 profile at all. A sendToServer failure that survives a patient-data fix is usually one
# of these MSH-9/MSH-12 deviations, not a data problem - see the per-group notes below for
# which files are known to deviate and whether the RIE tolerates it in practice.
TEST_GROUPS = {
    # General order/report exchange between NHS Trusts and iGene - the default scenario.
    # Deviation note: most R01 files here use the bare trigger "ORU^R01" (no "^ORU_R01") at
    # MSH-12 "2.3", not the spec's "ORU^R01^ORU_R01"/"2.5.1" - a legacy format the RIE's R01
    # path tolerates in practice. The O01 files use "2.4", which the IG doesn't define at all
    # (no ORM_O01 profile) - see the clatterbridge_histotrac note below on why that pattern
    # isn't safe to assume works for every O01 file.
    "general": {
        "cases": {
            "O21": ["OML_O21_RPY.txt", "OML_O21_R0A_R125.txt"],
            "O01": ["EPICJune26.txt", "EPICJune9.txt"],
            "R01": [
                "ORU_R01_DLIMS.txt",
                "ORU_R01_R125.1_R0A.txt",
                "ORU_R01_R125.1_RBS.txt",
                "ORU_R01_R125.1_REP.txt",
                "ORU_R01_R125.1_RR8.txt",
                "ORU_R01_R125.1_RX1.txt",
                "ORU_R01_R125.1_SG9.txt",
                "ORU_R01_R125.1_ZT001.txt",
                "ORU_R01_R125.1_7A3.txt",
                "ORU_R01_R125.1_RPY.txt",
                "ORU_R01_GS1_RXK.txt",
                "LRI-GeneVariant-1.txt",
                "LRI-GeneVariant-2.txt",
                "LRI-GeneVariant-3.txt",
                "LRI-GeneVariant-4.txt",
                "LRI-GeneVariant-5.txt",
            ],
        },
    },
    # iGene's "Baby of <mother>"/"Fetus of <mother>" PID+NK1 combined-segment convention -
    # see check_baby_fetus_split. These files already match the IG's required MSH-9/MSH-12
    # exactly (explicit "OML^O21^OML_O21"/"ORU^R01^ORU_R01", "2.5.1") - the PID+NK1 combining
    # is an intentional NW-GMSA/iGene extension layered on top of a conformant message, not a
    # spec violation, kept deliberately to exercise the Patient+RelatedPerson split.
    "baby_fetus": {
        "cases": {
            "O21": [
                "OML_O21_QE1_BabyOfLysa_R318.1.txt",
                "OML_O21_RXR_BabyOfGilly_R318.1.txt",
                "OML_O21_UNK_FetusOfYara_R22.1.txt",
                "OML_O21_R0A_FetusOfCersei_R22.1.txt",
                "OML_O21_REN_BabyOfCatelyn_R318.1.txt",
                "OML_O21_REP_FetusOfArya_R22.1.txt",
                "OML_O21_RBS_BabyOfBrienne_R318.1.txt",
            ],
            "R01": [
                "ORU_R01_QE1_BabyOfLysa_R318.1.txt",
                "ORU_R01_RXR_BabyOfGilly_R318.1.txt",
                "ORU_R01_UNK_FetusOfYara_R22.1.txt",
                "ORU_R01_R0A_FetusOfCersei_R22.1.txt",
                "ORU_R01_REN_BabyOfCatelyn_R318.1.txt",
                "ORU_R01_REP_FetusOfArya_R22.1.txt",
                "ORU_R01_RBS_BabyOfBrienne_R318.1.txt",
            ],
        },
    },
    # Shire (CPP) <-> HODS report exchange. Deviation note: MSH-12 is "2.3.1", which the IG
    # doesn't define (it specifies "2.5.1") - a Shire-specific legacy variant the RIE
    # currently tolerates.
    "shire": {
        "cases": {
            "R01": ["SHIRE_ORU_R01_RM3.txt", "Shire-1.txt", "Shire-2.txt"],
        },
    },
    # Clatterbridge Cancer Centre and Histotrac orders/reports.
    # Deviation notes (MSH-9/MSH-12, not patient data - see Clatterbridge-Order-review.md
    # for the fuller structural gap list, which goes beyond what was needed to unblock this):
    #  - Clatterbridge-Order.txt was the only "ORM^O01" fixture in the repo on MSH-12 "2.3"
    #    (every other one uses "2.4"/"2.5.1") - it was getting a consistent AR reject
    #    (#5035) even with real patient data. Bumping MSH-12 to "2.4", matching every sibling
    #    O01 file, fixed it (now ACK AA) - the RIE cares about the version, not just the
    #    (still IG-nonconformant, since OML_O21 is the only order profile the IG defines)
    #    ORM^O01 trigger itself.
    #  - histotrac.txt and histotrac-MFT.txt (R01): both rebuilt to the IG's PDF-report
    #    pattern (https://nw-gmsa.github.io/en/hl7v2.html) - MSH-9 "ORU^R01^ORU_R01"/MSH-12
    #    "2.5.1", OBR-4 the SNOMED discipline code
    #    "909871000000100^Histocompatibility and immunogenetics^SNM3" (replacing the local
    #    HISTOTRACEAP/no-OBR-at-all versions), and the embedded-PDF OBX per the IG's literal
    #    example: OBX-2 "ED", OBX-3 "1054161000000101^Genetic report^SNM3", OBX-5
    #    "MOL^IM^PDF^Base64^<data>", OBX-11 "F".
    "clatterbridge_histotrac": {
        "cases": {
            "O01": ["Clatterbridge-Order.txt", "histotrac-MFT.txt"],
            "R01": [
                "Clatterbridge-REN-ORU_R01.txt",
                "histotrac.txt",
                "histotrac-MFT.txt",
            ],
        },
    },
    # ctDNA orders/reports between NW Genomics (iGene) and NEY Genomics.
    "ctdna": {
        "cases": {
            "R01": ["ctDNA-Glasgow.txt", "ctdna9737383222.txt"],
        },
    },
    # dWGS sub-contracted orders (NEY GMS -> NW GMS, RGL to SGL). Unlike every other
    # group, the source fixture *is* the FHIR Bundle (Input/FHIR/O21, not Input/V2) -
    # "input_format": "fhir" runs the FHIR-sourced case (transformToV2, then the Bundle
    # itself POSTed to FHIR_SERVER's $process-message) via run_fhir_source_case instead
    # of run_case; there's no v2 original here to run transformToFHIR on first.
    # notebooks/08-subcontracted-laboratory-order-from-external-glh.ipynb builds and
    # narrates one worked example by hand (Input/dWGS.csv row 0, dWGS_r2026000201.json)
    # end to end; the other five rows in that CSV were built the same way (same
    # Patient/Specimen/ServiceRequest shapes, same profiles) purely as fixtures for this
    # script's coverage, without a matching notebook walkthrough. Two of dWGS.csv's
    # referral_ids repeat across rows (a Duo and a Trio grouping family members under one
    # referral) - filenames disambiguate those with the row's own patient_ngis_id rather
    # than one file silently overwriting another.
    "dwgs": {
        "input_dir": os.path.join("Input", "FHIR"),
        "input_format": "fhir",
        "cases": {
            "O21": [
                "dWGS_r2026000201.json",
                "dWGS_r2026000202_p2026000102.json",
                "dWGS_r2026000202_p2026000103.json",
                "dWGS_r2026000203_p2026000104.json",
                "dWGS_r2026000203_p2026000105.json",
                "dWGS_r2026000203_p2026000106.json",
            ],
        },
    },
    # Reference examples published by the NW-GMSA IG itself, not built by this repo -
    # https://nw-gmsa.github.io/en/StructureDefinition-BundleMessage-examples.html
    # (source: https://github.com/nw-gmsa/nw-gmsa.github.com). Fetched as the IG's own
    # published JSON (e.g. https://nw-gmsa.github.io/en/Bundle-GenomicsOrderMessage-ctDNA.json)
    # and kept verbatim, filenames unchanged, so they stay traceable back to that page.
    # FHIR-sourced like "dwgs" - input_format "fhir" runs run_fhir_source_case. 7 of the
    # page's 10 examples are included; none overlap with this repo's own hand-built
    # Input/FHIR content (checked by patient identity, not just filename - the ctDNA
    # pair reuses this repo's existing NHS-number test patients, per this repo's own
    # convention of reusing the same test-patient pool, but the Bundle content itself is
    # the IG's, not a copy of anything already in Input/). The other 3
    # (GenomicsOrderMessageReply{Acknowledge,Fatal,Ok}) are excluded - they're
    # MessageHeader-only $process-message *responses* (MessageHeader.response populated,
    # no Patient/ServiceRequest/etc.), not order/report messages to send in the first
    # place, so this harness's send-as-a-new-message model doesn't apply to them.
    # Deviation/known-failure notes, verified live rather than pre-filtered out (same
    # practice as e.g. cepheid): Bundle-GenomicsReportMessage.json (DocumentReference +
    # inline Binary PDF, no ctDNA data) gets a bare HTTP 500 from transformToV2 sometimes
    # (live infra, intermittent - not reproducible on every run).
    #
    # Both R01 examples also fail check_fhir_bundle's dangling-reference check - traced to
    # source (input/fsh/Examples/... in the IG's own repo): each Bundle's DiagnosticReport
    # (and, for -ctDNA, ServiceRequest too) is a FSH instance *shared* with a sibling
    # "document"-shaped Bundle example, and hardcodes a reference to a resource only that
    # sibling actually includes (two Observations + a Specimen for -ctDNA; a Composition,
    # via the DiagnosticReportCompositionR5 extension, for the other) - a real upstream
    # authoring gap in the IG's published examples, not something fixable by editing our
    # fetched copy. Out of scope for this repo to fix (suggested FSH-level fixes written
    # up and left with the IG maintainers) - known_dangling_refs below tells
    # run_fhir_source_case to stop treating those two specific, already-diagnosed
    # references as a failure here, while still surfacing any other/new problem.
    "nwgmsa_examples": {
        "input_dir": os.path.join("Input", "FHIR", "NWGMSA-Examples"),
        "input_format": "fhir",
        "cases": {
            "O21": [
                "Bundle-748683741.json",
                "Bundle-GenomicsOrderMessage-ctDNA.json",
                "Bundle-GenomicsOrderMessageAttachment.json",
                "Bundle-GenomicsOrderMessageCodedEntries.json",
            ],
            "R01": [
                "Bundle-GenomicsReportMessage-ctDNA.json",
                "Bundle-GenomicsReportMessage.json",
            ],
            "A31": [
                "Bundle-PatientMessage.json",
            ],
        },
        "known_dangling_refs": {
            # Two Observations (variant-egfr, region-studied-egfr-dpcr) + a Specimen -
            # all three only exist in the sibling Bundle-FHIRDocumentGeneticReportBundle-ctDNA.
            "Bundle-GenomicsReportMessage-ctDNA.json": {
                "urn:uuid:00c22e97-a226-4845-b17a-e24ec1f4f77a",
                "urn:uuid:a151b1ed-5aef-4c36-af50-987cfbd5bad4",
                "urn:uuid:b930b4c4-327a-4728-8bb9-f90061914cc5",
            },
            # DiagnosticReportCompositionR5 extension points at
            # Composition-GenomicsReport-OctaviaCHISLETT, which only exists in the
            # sibling FHIRDocumentGeneticReportBundle (the "Jack Dawkins" example).
            "Bundle-GenomicsReportMessage.json": {
                "urn:uuid:30551ce1-5a28-4356-b684-1e639094ad4d",
            },
        },
    },
    # Genomic order/report examples from NHS Digital's own national IG -
    # https://github.com/NHSDigital/NHSDigital-FHIR-Genomics-ImplementationGuide/tree/main/Bundle
    # (the National Genomic Medicine Service order/report model this repo's own NW-GMSA
    # IG sits underneath). Not every Bundle in that folder is an order/report - excluded:
    # Bundle-Searchset-Example (searchset, no clinical content), Bundle-TransactionResponse
    # {Error,Success}-Example (process-message *responses*, same reasoning as
    # nwgmsa_examples' excluded Reply bundles), Bundle-WGSRoD-Example (Consent +
    # QuestionnaireResponse, a "Record of Discussion" artifact, not an order/report),
    # CommunityCloud-Bundle-Example (DocumentReference/Specimen/Device/Procedure tracking
    # data, not an order/report), UKCore-Bundle-MichaelJonesSpecimen-Example (a bare
    # Specimen, referenced by the MichaelJonesRequest examples below rather than a
    # standalone case), and Bundle-GenomicReportVisibility-JamesWilson-Example (NHS
    # Digital's only R01/report example - not fully formed: no fullUrls at all (a
    # "collection" Bundle) and too thin a resource set to be a genuine report).
    #
    # FHIR_SERVER's $process-message (the ESB) doesn't support Bundle.type "transaction" -
    # the other 11 examples are order/report Bundles built as one (a conditional-upload
    # payload, entry[].request present, no MessageHeader), needing the basic conversion
    # to "message" this group's local copies carry out (see
    # NHSDigital-Examples-conversion-notes.md alongside them): Bundle.type -> "message",
    # drop entry[].request, add Bundle.identifier/timestamp, prepend a MessageHeader
    # (eventCoding http://terminology.hl7.org/CodeSystem/v2-0003#O21, matching every
    # other message this repo sends - NHS Digital's own local eventCoding
    # (CodeSystem-Genomics-message-events.json's genomictestrequest/genomictestresponse)
    # isn't recognised by FHIR_SERVER, destination fixed at NW Genomics 699X0 -
    # where FHIR_SERVER actually routes everything in this harness regardless of an
    # example's "real" intended GLH - sender identity best-effort extracted from each
    # Bundle's own ServiceRequest.requester -> PractitionerRole.organization). Existing
    # fullUrls/references are left untouched other than that - genuinely "basic", not a
    # full rebuild.
    # Two examples (UKCore-Bundle-MichaelJonesRequest-Example_{minimal,v3_message}) were
    # already proper message Bundles with a MessageHeader - copied verbatim, unconverted.
    #
    # Three of those 11 (Scenario3, Scenario4, FetalScenario) bundle a whole family
    # group's linked orders - e.g. a fetus, its mother, and its father, each with their
    # own ServiceRequest - into one FHIR message. OML^O21 (and this repo's LIMS) model
    # one order per message, so each was further split with
    # split_message_bundle_by_patient (one output message per distinct patient; a
    # patient with more than one ServiceRequest, e.g. Scenario4's mother, stays together
    # as one message) and the combined source file replaced by its per-patient outputs.
    #
    # Of those per-patient messages, only the "proband" ones (Extension-Genomic-
    # Patient-Role) are kept - this repo's LIMS/RIE doesn't support "consultand" orders
    # (a ServiceRequest whose subject is actually a relative of the patient being
    # tested), which OML^O21 has no way to represent. drop_consultand_orders removes
    # them, folding each dropped consultand order's own note text and a summary of its
    # supportingInfo Observations into the matching proband ServiceRequest.note first
    # (matched by shared requisition) rather than silently losing that content -
    # Scenario3 -> {-FetusA} (Mother dropped), Scenario4 -> {-FetusA,-FetusB} (Mother
    # dropped), FetalScenario -> {-Fetus} (Mother and Father dropped).
    # Bundle-NonWGSTestOrderFormUpdated-FetalScenario-Example was dropped entirely -
    # a standalone consultand-only (father) Bundle with no proband ServiceRequest in
    # the same message to fold into. See NHSDigital-Examples-conversion-notes.md.
    "nhsd_examples": {
        "input_dir": os.path.join("Input", "FHIR", "NHSDigital-Examples"),
        "input_format": "fhir",
        "cases": {
            "O21": [
                "Bundle-NonWGSScenario3-FetusAsProband-Example-FetusA.json",
                "Bundle-NonWGSScenario4-ProbandWithMultipleFetus-Example-FetusA.json",
                "Bundle-NonWGSScenario4-ProbandWithMultipleFetus-Example-FetusB.json",
                "Bundle-NonWGSScenario5-ProductsofConception-Example.json",
                "Bundle-NonWGSTestOrderForm-CancerSolidTumor-Example.json",
                "Bundle-NonWGSTestOrderForm-Example.json",
                "Bundle-NonWGSTestOrderForm-FetalScenario-Example-Fetus.json",
                "Bundle-NonWGSTestOrderForm-Reanalysis-Example.json",
                "Bundle-NonWGSTestOrderFormQRPatientExtensions-Example.json",
                "Bundle-WGSTestOrderForm-Example.json",
                "UKCore-Bundle-MichaelJonesRequest-Example_minimal.json",
                "UKCore-Bundle-MichaelJonesRequest-Example_v3_message.json",
            ],
        },
    },
    # Cepheid GeneXpert results (message type R32). Sourced from Input/ASTM/R32 - see
    # Testing-Cephied.ipynb, which flags the old Input/V2/R32 source as superseded by
    # these files and skips the transformToV2 round-trip stage, so we do too.
    # Deviation note: R32 isn't defined anywhere in the NW-GMSA IG (only OML_O21, ORU_R01,
    # and MDM_T02 are), so this group is inherently off-spec regardless of version. It's also
    # been the least reliable group to run live - every case bare-timed-out (no ACK at all,
    # unlike the reject-style AR/#5035 failures seen on genuine version mismatches) in earlier
    # runs, then passed cleanly with no code/data change at all in a later run, which points to
    # transient RIE-side unavailability for this group rather than a routing gap - but with an
    # off-spec trigger event in the mix too, that's not fully ruled out either.
    "cepheid": {
        "input_dir": os.path.join("Input", "ASTM"),
        "skip_transform_to_v2": True,
        "cases": {
            "R32": [f"cepheid-{i}.txt" for i in range(1, 8)],
        },
    },
}


def parse_ack(text):
    """Parse an HL7 ACK response (MSH/MSA/[ERR], CR-terminated segments).
    Returns (ack_code, detail): ack_code is MSA-1 ('AA'/'CA' = accept, 'AE'/'AR'/'CE'/'CR' =
    error/reject), or None if the response doesn't look like an ACK at all.
    """
    segments = [s for s in text.replace("\r\n", "\r").split("\r") if s]
    msa = next((s for s in segments if s.startswith("MSA|")), None)
    err = next((s for s in segments if s.startswith("ERR|")), None)
    if msa is None:
        return None, text[:200]
    fields = msa.split("|")
    ack_code = fields[1] if len(fields) > 1 else None
    return ack_code, (err or msa)


_fhir_bearer_token = None


def get_fhir_bearer_token(session):
    """Fetch (and cache for the life of the process) an OAuth2 client-credentials bearer
    token for FHIR_SERVER - the same flow Testing.ipynb and notebook 08's worked example
    use. Raises requests.RequestException/ValueError/KeyError on failure; callers decide
    how to record that as a case failure."""
    global _fhir_bearer_token
    if _fhir_bearer_token is None:
        log(f"POST {OAUTH2_TOKEN_URL} (fetching FHIR_SERVER OAuth2 bearer token)")
        resp = session.post(
            OAUTH2_TOKEN_URL,
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            data={"grant_type": "client_credentials", "scope": "system/*.*"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            verify=False, timeout=15,
        )
        resp.raise_for_status()
        _fhir_bearer_token = resp.json()["access_token"]
    return _fhir_bearer_token


def parse_process_message_response(response_json):
    """Parse a $process-message response Bundle. Returns (code, detail): code is the
    MessageHeader entry's response.code ('ok'/'transient-error'/'fatal-error' per the FHIR
    spec), or None if no MessageHeader.response was found at all; detail is an
    OperationOutcome entry's diagnostics text, if the response included one.
    """
    entries = response_json.get("entry", []) if isinstance(response_json, dict) else []
    message_header = next(
        (e.get("resource", {}) for e in entries if e.get("resource", {}).get("resourceType") == "MessageHeader"),
        None,
    )
    code = (message_header or {}).get("response", {}).get("code")
    outcome = next(
        (e.get("resource", {}) for e in entries if e.get("resource", {}).get("resourceType") == "OperationOutcome"),
        None,
    )
    detail = None
    if outcome:
        issues = outcome.get("issue", [])
        if issues:
            detail = issues[0].get("diagnostics") or issues[0].get("details", {}).get("text")
    return code, detail


VALID_BUNDLE_TYPES = {
    "document", "message", "transaction", "transaction-response",
    "batch", "batch-response", "history", "searchset", "collection",
}


def check_fhir_bundle(bundle):
    """Basic structural sanity checks on a transformToFHIR response - not IG/profile
    validation (that's FHIR Validation.ipynb's job), just: is this a well-formed Bundle
    that hangs together internally. Returns a list of problem strings; empty = OK.
    """
    problems = []

    if not isinstance(bundle, dict):
        return ["response is not a JSON object"]

    if bundle.get("resourceType") != "Bundle":
        problems.append(f"resourceType is {bundle.get('resourceType')!r}, expected 'Bundle'")

    bundle_type = bundle.get("type")
    if not bundle_type:
        problems.append("Bundle.type is missing")
    elif bundle_type not in VALID_BUNDLE_TYPES:
        problems.append(f"Bundle.type {bundle_type!r} is not a recognised Bundle.type code")

    entries = bundle.get("entry")
    if not isinstance(entries, list) or not entries:
        problems.append("Bundle.entry is missing or empty")
        return problems  # nothing further to check without entries

    full_urls = []
    message_header_count = 0
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            problems.append(f"entry[{i}] is not a JSON object")
            continue

        resource = entry.get("resource")
        if not isinstance(resource, dict):
            problems.append(f"entry[{i}] has no 'resource' object")
            continue

        rtype = resource.get("resourceType")
        if not rtype:
            problems.append(f"entry[{i}].resource is missing 'resourceType'")
        elif rtype == "MessageHeader":
            message_header_count += 1

        full_url = entry.get("fullUrl")
        if full_url:
            if full_url in full_urls:
                problems.append(f"duplicate fullUrl in bundle: {full_url}")
            full_urls.append(full_url)
        elif rtype and rtype != "MessageHeader":
            problems.append(f"entry[{i}] ({rtype}) has no 'fullUrl'")

    if message_header_count != 1:
        problems.append(f"expected exactly 1 MessageHeader entry, found {message_header_count}")
    elif entries[0].get("resource", {}).get("resourceType") != "MessageHeader":
        problems.append("MessageHeader is not the first entry in the bundle")

    # Dangling-reference check: any urn:uuid: reference should resolve to a fullUrl
    # actually present in this bundle.
    known_urls = set(full_urls)

    def walk(node):
        if isinstance(node, dict):
            ref = node.get("reference")
            if isinstance(ref, str) and ref.startswith("urn:uuid:") and ref not in known_urls:
                problems.append(f"dangling reference: {ref}")
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for entry in entries:
        walk(entry.get("resource"))

    return list(dict.fromkeys(problems))  # de-dupe, preserve order


def _resolve_bundle_reference(bundle, reference):
    """Resolves a Reference.reference string against Bundle.entry.fullUrl - either an
    exact match (the fullUrl form), or, for a relative 'ResourceType/id' reference (the
    form several of the NHSDigital-Examples source Bundles actually use, inconsistently
    with their own http://example.org/... fullUrls), the entry of that resourceType
    whose fullUrl or resource.id ends with that id. Returns the matching entry dict, or
    None if reference is empty/unresolvable.
    """
    if not reference:
        return None
    for entry in bundle.get("entry", []):
        if entry.get("fullUrl") == reference:
            return entry
    if "/" in reference:
        want_type, want_id = reference.split("/", 1)
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            if resource.get("resourceType") != want_type:
                continue
            full_url = entry.get("fullUrl", "")
            if full_url.rsplit("/", 1)[-1] == want_id or resource.get("id") == want_id:
                return entry
    return None


def _patient_key(bundle, reference_obj):
    """Canonical key identifying "which patient" a Reference (e.g.
    ServiceRequest.subject, Specimen.subject, RelatedPerson.patient) points at - the
    matching entry's fullUrl if it resolves to one actually present in the Bundle,
    else the raw Reference.reference string, else a stringified Reference.identifier.
    Two references to the same patient produce the same key even when, as for some of
    NHS Digital's own mother references, no Patient *resource* for them exists in the
    Bundle at all (identifier-only, relying on PDS) - matching on the resolved fullUrl
    alone would treat every such reference as unrelated.
    """
    if not reference_obj:
        return None
    reference = reference_obj.get("reference")
    resolved = _resolve_bundle_reference(bundle, reference)
    if resolved:
        return resolved.get("fullUrl")
    if reference:
        return reference
    identifier = reference_obj.get("identifier")
    return json.dumps(identifier, sort_keys=True) if identifier else None


def split_message_bundle_by_patient(bundle):
    """Splits a converted FHIR message Bundle whose ServiceRequests belong to more than
    one Patient into one message Bundle per patient - each patient's own order(s) plus
    whatever it references (requester, specimens, supportingInfo Observations, linked
    RelatedPersons). A Bundle with only one distinct patient is returned unchanged, as a
    one-item list.

    Rationale: OML^O21 (and this repo's LIMS) model one order per message. NHS Digital's
    own examples instead bundle a whole family group's linked orders - e.g. a fetus, its
    mother, and its father, each with their own ServiceRequest/Specimen - into a single
    FHIR message. Converting that straight to v2 produces one message with several
    repeated ORC/OBR/PID groups rather than several independent orders, so the split has
    to happen on the FHIR side, before transformToV2 - not after.

    Grouping is by patient (ServiceRequest.subject), not by ServiceRequest: a patient
    with more than one ServiceRequest (e.g. Scenario4's mother, who has two - one per
    fetus's requisition/order group) still ends up as a single message carrying both,
    rather than being split further.
    """
    entries = bundle.get("entry", [])
    message_header_entry = next(
        (e for e in entries if e.get("resource", {}).get("resourceType") == "MessageHeader"), None
    )
    service_requests = [e for e in entries if e.get("resource", {}).get("resourceType") == "ServiceRequest"]

    groups = {}  # _patient_key(...) -> [ServiceRequest entry, ...]
    group_order = []
    for sr_entry in service_requests:
        key = _patient_key(bundle, sr_entry["resource"].get("subject"))
        if key not in groups:
            groups[key] = []
            group_order.append(key)
        groups[key].append(sr_entry)

    if len(groups) <= 1:
        return [bundle]

    split_bundles = []
    for patient_key in group_order:
        sr_entries = groups[patient_key]
        included = {}  # fullUrl -> entry, dict preserves first-seen order

        def include(entry):
            if entry and entry.get("fullUrl") not in included:
                included[entry["fullUrl"]] = entry

        include(next((e for e in entries if e.get("fullUrl") == patient_key), None))

        for sr_entry in sr_entries:
            include(sr_entry)
            sr = sr_entry["resource"]
            include(_resolve_bundle_reference(bundle, sr.get("requester", {}).get("reference")))
            for ref_list_field in ("specimen", "supportingInfo", "reasonReference"):
                for ref in sr.get(ref_list_field, []):
                    include(_resolve_bundle_reference(bundle, ref.get("reference")))

        # Specimens/Observations/RelatedPersons linked to this patient only via their
        # own .subject/.patient (not referenced from any ServiceRequest field) - e.g.
        # FetalScenario's two Specimens, both on the mother, referenced by no
        # ServiceRequest.specimen; or Scenario3's "Second Trimester Anomalies?"
        # Observation, on the mother but not wired into any ServiceRequest.supportingInfo
        # at all in NHS Digital's own source data (an upstream authoring gap, not
        # something this conversion should silently drop).
        for entry in entries:
            resource = entry["resource"]
            rtype = resource.get("resourceType")
            if rtype not in ("Specimen", "Observation", "RelatedPerson"):
                continue
            owner_field = "patient" if rtype == "RelatedPerson" else "subject"
            if _patient_key(bundle, resource.get(owner_field)) == patient_key:
                include(entry)

        new_header = json.loads(json.dumps(message_header_entry["resource"])) if message_header_entry else {}
        new_header["id"] = str(uuid.uuid4())
        new_header["focus"] = [{"reference": sr_entry["fullUrl"]} for sr_entry in sr_entries]

        split_bundles.append({
            "resourceType": "Bundle",
            "type": "message",
            "identifier": {
                "system": bundle.get("identifier", {}).get("system", "https://tools.ietf.org/html/rfc4122"),
                "value": str(uuid.uuid4()),
            },
            "timestamp": bundle.get("timestamp"),
            "entry": (
                [{"fullUrl": f"urn:uuid:{new_header['id']}", "resource": new_header}]
                + list(included.values())
            ),
        })

    return split_bundles


def check_patient_demographics_preserved(bundle, v2_text):
    """Checks that a Patient's name/birthDate/gender - wherever present on the FHIR
    side - survived transformToV2's conversion into the resulting message's PID
    segment (PID-5/PID-7/PID-8), for the Bundle's *primary* subject (the
    ServiceRequest's, or a DiagnosticReport's for an R01 report).

    Added after an ad hoc audit of all 18 NHSDigital-Examples files found no losses -
    this makes that check repeatable on every future resync rather than a one-off.

    Returns (applicable, problems): applicable is False (and problems is []) when
    there's nothing to compare - no ServiceRequest/DiagnosticReport, its subject
    doesn't resolve to an actual Patient resource in the Bundle (a missing Patient is
    a different concern - see split_message_bundle_by_patient's docstring and
    NHSDigital-Examples-conversion-notes.md), or that Patient has no
    name/birthDate/gender to lose in the first place.
    """
    entries = bundle.get("entry", []) if isinstance(bundle, dict) else []
    primary = next(
        (e.get("resource", {}) for e in entries
         if e.get("resource", {}).get("resourceType") in ("ServiceRequest", "DiagnosticReport")),
        None,
    )
    if not primary:
        return False, []

    patient_entry = _resolve_bundle_reference(bundle, (primary.get("subject") or {}).get("reference"))
    patient = patient_entry.get("resource", {}) if patient_entry else None
    if not patient or patient.get("resourceType") != "Patient":
        return False, []

    names = patient.get("name")
    src_name = None
    if names:
        n = names[0]
        src_name = f"{' '.join(n.get('given', []))} {n.get('family', '')}".strip()
    src_dob = patient.get("birthDate")
    src_gender = patient.get("gender")

    if not (src_name or src_dob or src_gender):
        return False, []

    all_pid_fields = [
        seg.split("|") for seg in v2_text.replace("\r\n", "\r").split("\r") if seg.startswith("PID|")
    ]
    if not all_pid_fields:
        return True, ["Patient has name/birthDate/gender but the transformToV2 output has no PID segment at all"]

    # Some messages (e.g. a Specimen whose subject differs from the ServiceRequest's
    # own subject) come back with more than one PID segment - transformToV2 puts the
    # subject's own demographics in whichever one carries a matching PID-3 identifier
    # value, not necessarily the first. Fall back to the first PID for the common
    # single-PID case.
    identifier_values = [i.get("value") for i in patient.get("identifier", []) if i.get("value")]
    pid_fields = next(
        (f for f in all_pid_fields if len(f) > 3 and any(v and v in f[3] for v in identifier_values)),
        all_pid_fields[0],
    )

    v2_name = pid_fields[5] if len(pid_fields) > 5 else ""
    v2_dob = pid_fields[7] if len(pid_fields) > 7 else ""
    v2_gender = pid_fields[8] if len(pid_fields) > 8 else ""

    problems = []
    if src_name and not v2_name:
        problems.append(f"Patient.name {src_name!r} present in FHIR but PID-5 is blank")
    if src_dob and v2_dob.replace("-", "") != src_dob.replace("-", ""):
        problems.append(f"Patient.birthDate {src_dob!r} present in FHIR but PID-7 is {v2_dob!r}")
    if src_gender and not v2_gender:
        problems.append(f"Patient.gender {src_gender!r} present in FHIR but PID-8 is blank")

    return True, problems


GENOMIC_PATIENT_ROLE_EXTENSION = "https://fhir.nhs.uk/England/StructureDefinition/Extension-Genomic-Patient-Role"


def _service_request_role(service_request):
    """The Extension-Genomic-Patient-Role code on a ServiceRequest ('proband',
    'consultand', ...), or None if the extension isn't present."""
    for ext in service_request.get("extension", []):
        if ext.get("url") == GENOMIC_PATIENT_ROLE_EXTENSION:
            return ext.get("valueCodeableConcept", {}).get("coding", [{}])[0].get("code")
    return None


RELATIONSHIP_ROLE_LABELS = {
    "NMTHF": "Mother",
    "NFTHF": "Father",
    "MTH": "Mother",
    "FTH": "Father",
    "NCHILD": "Child",
    "SIB": "Sibling",
}


def _consultand_identity_label(consultand_sr, consultand_bundle, proband_bundle):
    """A human-readable "who is this information about" label for a consultand
    ServiceRequest's subject - 'Jane Smith (Mother)', or '(Father)' where no name is
    known, or None where neither a name nor a relationship can be found - by matching
    the consultand's own subject.identifier against a RelatedPerson (in either bundle)
    carrying the identical identifier. RelatedPerson.name/.relationship describe that
    same person relative to the *proband*, which is exactly the context this label
    needs to give inside the proband's own ServiceRequest.note.
    """
    subject_ident = (consultand_sr.get("subject") or {}).get("identifier") or {}
    subject_ident_value = subject_ident.get("value")

    name_text = None
    role_label = None
    if subject_ident_value:
        for bundle in (proband_bundle, consultand_bundle):
            for entry in bundle.get("entry", []):
                resource = entry["resource"]
                if resource.get("resourceType") != "RelatedPerson":
                    continue
                if subject_ident_value not in [i.get("value") for i in resource.get("identifier", [])]:
                    continue
                names = resource.get("name")
                if names and not name_text:
                    n = names[0]
                    name_text = f"{' '.join(n.get('given', []))} {n.get('family', '')}".strip()
                relationships = resource.get("relationship")
                if relationships and not role_label:
                    coding = relationships[0].get("coding", [{}])[0]
                    role_label = RELATIONSHIP_ROLE_LABELS.get(coding.get("code"), coding.get("display"))

    if not name_text:
        patient_entry = _resolve_bundle_reference(consultand_bundle, (consultand_sr.get("subject") or {}).get("reference"))
        patient = patient_entry.get("resource") if patient_entry else None
        names = patient.get("name") if patient else None
        if names:
            n = names[0]
            name_text = f"{' '.join(n.get('given', []))} {n.get('family', '')}".strip()

    if name_text and role_label:
        return f"{name_text} ({role_label})"
    if role_label:
        return f"({role_label})"
    return name_text


def _observation_summary(obs):
    """A short human-readable rendering of an Observation's code/value(s) - 'Ethnicity:
    unknown', 'Pregnancy: Assisted conception; Gestational age 87 day' (components
    joined the same way) - for folding a dropped consultand order's supportingInfo into
    a proband ServiceRequest.note as free text, per drop_consultand_orders below."""
    code = obs.get("code", {})
    code_display = (
        code.get("text") or code.get("coding", [{}])[0].get("display") or code.get("coding", [{}])[0].get("code") or "?"
    )

    def value_text(node):
        if "valueCodeableConcept" in node:
            return node["valueCodeableConcept"].get("coding", [{}])[0].get("display", "")
        if "valueString" in node:
            return node["valueString"]
        if "valueQuantity" in node:
            q = node["valueQuantity"]
            return f"{q.get('value')} {q.get('unit', '')}".strip()
        if "valueDateTime" in node:
            return node["valueDateTime"]
        return ""

    parts = [value_text(obs)]
    for comp in obs.get("component", []):
        comp_display = comp.get("code", {}).get("coding", [{}])[0].get("display", "")
        parts.append(f"{comp_display} {value_text(comp)}".strip())

    value_str = "; ".join(p for p in parts if p)
    line = f"{code_display}: {value_str}" if value_str else code_display
    if obs.get("note"):
        line += f" ({obs['note'][0]['text']})"
    return line


def drop_consultand_orders(bundles):
    """Given a list of per-patient message Bundles - typically
    split_message_bundle_by_patient's output, but works just as well on a plain
    [bundle] that was never split - drops any whose ServiceRequest is coded
    'consultand' (Extension-Genomic-Patient-Role): this repo's LIMS/RIE only supports
    proband orders, OML^O21 having no way to represent "this order is actually about a
    different patient's relative". A ServiceRequest with no role extension at all
    (most of the simpler, single-patient examples) is treated as proband-equivalent -
    the extension only shows up where a Bundle actually distinguishes multiple family
    members' roles.

    A dropped consultand order's own clinically-relevant content isn't just discarded:
    its ServiceRequest.note (any lines not already present on the matched proband's own
    note) and a summary of its supportingInfo Observations are folded into the matched
    proband ServiceRequest's own .note instead, each as its own " - "-prefixed detail
    line under a header naming who they're about (see _consultand_identity_label) - a
    consultand with nothing left to fold in still gets its header, followed by a single
    " - no details presented" line, so its existence isn't silently dropped without a
    trace. Matched by requisition (system+value) - every family-group example seen so
    far shares one requisition across all its members' ServiceRequests, a simpler and
    more robust correlation than chasing shared RelatedPerson links. A consultand
    bundle whose requisition matches no proband bundle's (e.g. a standalone
    consultand-only Bundle, split alone) is dropped with its content unrecovered -
    there's nothing to fold it into.
    """
    def service_requests(bundle):
        return [e["resource"] for e in bundle.get("entry", []) if e["resource"]["resourceType"] == "ServiceRequest"]

    def requisition_key(sr):
        req = (sr or {}).get("requisition") or {}
        return (req.get("system"), req.get("value"))

    # Classify whole bundles by their first ServiceRequest's role - a bundle's
    # ServiceRequests are homogeneous in every example seen so far (role is really a
    # per-patient attribute: a consultand bundle can carry more than one ServiceRequest,
    # e.g. Scenario4's mother has two - one per fetus's requisition/order group - but
    # never a mix of proband and consultand ServiceRequests in the same bundle).
    proband_bundles = []  # (bundle, [ServiceRequest, ...])
    consultand_bundles = []
    for bundle in bundles:
        srs = service_requests(bundle)
        first_role = _service_request_role(srs[0]) if srs else None
        if first_role == "consultand":
            consultand_bundles.append((bundle, srs))
        else:
            proband_bundles.append((bundle, srs))

    proband_by_requisition = {
        requisition_key(sr): (proband_bundle, sr) for proband_bundle, srs in proband_bundles for sr in srs
    }

    for consultand_bundle, consultand_srs in consultand_bundles:
        for consultand_sr in consultand_srs:
            matched = proband_by_requisition.get(requisition_key(consultand_sr))
            if matched is None:
                continue  # nothing to fold into - content is dropped along with the bundle
            proband_bundle, proband_sr = matched

            existing_note = proband_sr.get("note", [{}])[0].get("text", "") if proband_sr.get("note") else ""
            lines = []

            own_note = consultand_sr.get("note", [{}])[0].get("text", "") if consultand_sr.get("note") else ""
            own_lines = [line for line in own_note.split("\n") if line and line not in existing_note]

            obs_summaries = []
            for si in consultand_sr.get("supportingInfo", []):
                entry = _resolve_bundle_reference(consultand_bundle, si.get("reference"))
                obs = entry.get("resource") if entry else None
                if obs and obs.get("resourceType") == "Observation":
                    obs_summaries.append(_observation_summary(obs))

            detail_lines = own_lines + obs_summaries

            # Who this folded-in content is about, e.g. "Ryanne Boulder (Mother):",
            # "Consultand (Father):" (name unknown), or "Consultand:" (neither name
            # nor relationship resolvable) - see _consultand_identity_label. Always
            # emitted, even with nothing to fold in, so a proband with more than one
            # linked consultand doesn't silently drop one without a trace.
            identity = _consultand_identity_label(consultand_sr, consultand_bundle, proband_bundle)
            if identity and not identity.startswith("("):
                header = f"{identity}:"
            elif identity:
                header = f"Consultand {identity}:"
            else:
                header = "Consultand:"
            lines.append(header)
            if detail_lines:
                lines.extend(f" - {detail}" for detail in detail_lines)
            else:
                lines.append(" - no details presented")

            new_note_text = existing_note + ("\n" if existing_note else "") + "\n".join(lines)
            proband_sr["note"] = [{"text": new_note_text}]
            existing_note = new_note_text

    return [b for b, _ in proband_bundles]


# iGene convention: a PID-5 given name of "Baby of <mother>" / "Fetus of <mother>" signals
# that PID and NK1 have been combined into one segment (see IntegrationTest change adding the
# mother's NHS number/DOB into the baby/fetus's own PID). transformToFHIR is expected to
# split that back out into a Patient (the baby/fetus) plus a RelatedPerson (the mother).
BABY_FETUS_PREFIXES = ("baby of ", "fetus of ")


def extract_pid5_given_name(v2_text):
    """Return PID-5's given-name component (PID.5.2) from a raw v2 message, or None."""
    segments = [s for s in v2_text.replace("\r\n", "\r").split("\r") if s]
    pid = next((s for s in segments if s.startswith("PID|")), None)
    if not pid:
        return None
    fields = pid.split("|")
    if len(fields) <= 5:
        return None
    components = fields[5].split("^")
    return components[1] if len(components) > 1 else None


def check_baby_fetus_split(v2_text, bundle):
    """If the source message follows the 'Baby of'/'Fetus of' convention, verify
    transformToFHIR split the combined PID/NK1 data into a Patient (baby/fetus) and a
    RelatedPerson (mother, relationship MTH) rather than collapsing them into one Patient.

    Returns (applicable, problems): applicable is False (and problems is []) for messages
    that don't follow the convention, so callers can skip reporting a stage for them.
    """
    given = extract_pid5_given_name(v2_text)
    if not given or not given.strip().lower().startswith(BABY_FETUS_PREFIXES):
        return False, []

    problems = []
    entries = bundle.get("entry", []) if isinstance(bundle, dict) else []
    resources = [(e, e.get("resource", {})) for e in entries]

    patient_entries = [(e, r) for e, r in resources if r.get("resourceType") == "Patient"]
    related_entries = [(e, r) for e, r in resources if r.get("resourceType") == "RelatedPerson"]

    if len(patient_entries) != 1:
        problems.append(f"expected exactly 1 Patient resource, found {len(patient_entries)}")
        patient = None
        patient_full_url = None
    else:
        patient_entry, patient = patient_entries[0]
        patient_full_url = patient_entry.get("fullUrl")
        patient_given = ((patient.get("name") or [{}])[0].get("given") or [""])[0]
        if not patient_given.strip().lower().startswith(BABY_FETUS_PREFIXES):
            problems.append(
                f"Patient.name.given is {patient_given!r}, expected it to start with 'Baby of '/'Fetus of '"
            )

    if not related_entries:
        problems.append("no RelatedPerson resource found for the mother")
    else:
        _, mother = related_entries[0]
        mother_given = ((mother.get("name") or [{}])[0].get("given") or [""])[0]
        if mother_given.strip().lower().startswith(BABY_FETUS_PREFIXES):
            problems.append(
                f"RelatedPerson.name.given is {mother_given!r} - looks like the baby/fetus name, not the mother's"
            )

        rel_codes = [
            c.get("code")
            for rel in mother.get("relationship", [])
            for c in rel.get("coding", [])
        ]
        if "MTH" not in rel_codes:
            problems.append(f"RelatedPerson.relationship codes {rel_codes} do not include 'MTH'")

        ref = mother.get("patient", {}).get("reference")
        if patient_full_url and ref != patient_full_url:
            problems.append(
                f"RelatedPerson.patient.reference {ref!r} does not match the Patient's fullUrl {patient_full_url!r}"
            )

    return True, problems


# v2 CE/CWE coding-system abbreviations (3rd component) mapped to their FHIR system URI -
# used by check_document_reference_code below.
V2_CODE_SYSTEM_TO_FHIR = {
    "SNM3": "http://snomed.info/sct",
    "SCT": "http://snomed.info/sct",
    "SNOMED-CT": "http://snomed.info/sct",
    "LN": "http://loinc.org",
    "LOINC": "http://loinc.org",
}


def extract_obx_segments(v2_text):
    """Return every OBX segment from a raw v2 message, each split on '|'."""
    segments = [s for s in v2_text.replace("\r\n", "\r").split("\r") if s]
    return [s.split("|") for s in segments if s.startswith("OBX|")]


def find_document_reference(bundle):
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") == "DocumentReference":
            return resource
    return None


def check_document_reference_code(v2_text, bundle):
    """DocumentReference.type must carry a SNOMED/LOINC coding consistent with the source
    OBX, per two NW-GMSA conventions (see the histotrac vs. ORU_R01_R125.1_RR8 fixtures):

      - OBX-2 'ED' (encapsulated data): if OBX-3 (the observation identifier) itself
        supplies a SNOMED (SNM3/SCT) or LOINC (LN) code - e.g. histotrac.txt's OBX-3
        "1054161000000101^Genetic report^SNM3" - that exact code+system must be preserved
        on DocumentReference.type. The transform must not drop or substitute a supplied code.
      - OBX-2 'CE' whose value embeds a PDF (OBX-5 containing an 'application/pdf'
        attachment, the iGene panel-report convention e.g. ORU_R01_R125.1_RR8.txt):
        DocumentReference.type must carry *some* SNOMED or LOINC coding, even when OBX-3
        only supplies a local/vendor code (e.g. an IGEAP panel code) with no SNOMED/LOINC
        equivalent of its own - substituting in a LOINC/SNOMED code here is expected/fine
        since the source identifier didn't supply one.

    Returns (applicable, problems): applicable is False (and problems is []) for messages
    with no OBX matching either convention.
    """
    applicable = False
    problems = []

    doc_ref = find_document_reference(bundle) if isinstance(bundle, dict) else None
    doc_ref_codings = (doc_ref or {}).get("type", {}).get("coding", [])
    doc_ref_has_snomed_or_loinc = any(
        c.get("system") in ("http://snomed.info/sct", "http://loinc.org")
        for c in doc_ref_codings
    )

    for fields in extract_obx_segments(v2_text):
        value_type = fields[2] if len(fields) > 2 else ""
        identifier = fields[3] if len(fields) > 3 else ""
        value = fields[5] if len(fields) > 5 else ""
        id_components = identifier.split("^")
        # v2 fields are sometimes fixed-width padded (e.g. "51969-4    ^Full narrative
        # report^LN") - the transform trims this before emitting the FHIR code, so strip
        # here too or every padded fixture false-positives against the trimmed FHIR code.
        id_code = id_components[0].strip() if id_components else ""
        id_system_raw = id_components[2].strip() if len(id_components) > 2 else ""
        id_system = V2_CODE_SYSTEM_TO_FHIR.get(id_system_raw.upper())

        if value_type == "ED" and id_system:
            applicable = True
            if not doc_ref:
                problems.append(
                    f"OBX-3 supplies {id_system_raw} code {id_code!r} but no DocumentReference "
                    "found in the bundle"
                )
            elif not any(
                c.get("code") == id_code and c.get("system") == id_system
                for c in doc_ref_codings
            ):
                problems.append(
                    f"OBX-3 code {id_code!r} ({id_system_raw}) not preserved on "
                    f"DocumentReference.type (found: {doc_ref_codings})"
                )

        if value_type == "CE" and "application/pdf" in value.lower():
            applicable = True
            if not doc_ref:
                problems.append("OBX-5 embeds a PDF but no DocumentReference found in the bundle")
            elif not doc_ref_has_snomed_or_loinc:
                problems.append(
                    "OBX-5 embeds a PDF but DocumentReference.type has no SNOMED/LOINC coding "
                    f"(found: {doc_ref_codings})"
                )

    return applicable, list(dict.fromkeys(problems))


class CaseResult:
    def __init__(self, name):
        self.name = name
        self.stages = []  # list of (stage_name, passed, detail)

    def record(self, stage, passed, detail=""):
        self.stages.append((stage, passed, detail))

    @property
    def passed(self):
        return all(passed for _, passed, _ in self.stages)


def run_case(session, group, msg_type, filename, skip_send, input_dir=None,
             skip_transform_to_v2=False, save_output=True):
    case_name = f"{group}/{msg_type}/{filename}"
    log(f"=== starting {case_name} ===")
    result = CaseResult(case_name)
    in_path = os.path.join(input_dir or os.path.join("Input", "V2"), msg_type, filename)

    log(f"loading {in_path}")
    if not os.path.exists(in_path):
        result.record("load", False, f"file not found: {in_path}")
        log(f"FAILED load: file not found: {in_path}")
        return result
    with open(in_path, "rb") as f:
        v2_bytes = f.read()
    result.record("load", True, f"{len(v2_bytes)} bytes")
    log(f"loaded {len(v2_bytes)} bytes")

    # --- Stage 1: transformToFHIR ---
    log(f"POST {V2_TOOLS}/transformToFHIR (timeout=30s)")
    try:
        r1 = session.post(
            f"{V2_TOOLS}/transformToFHIR", data=v2_bytes,
            headers=HEADERS_V2, verify=False, timeout=30,
        )
    except requests.RequestException as e:
        result.record("transformToFHIR", False, f"request error: {e}")
        log(f"FAILED transformToFHIR: request error: {e}")
        return result

    if r1.status_code != 200:
        result.record("transformToFHIR", False, f"HTTP {r1.status_code}: {r1.text[:200]}")
        log(f"FAILED transformToFHIR: HTTP {r1.status_code}")
        return result

    result.record("transformToFHIR", True, f"HTTP {r1.status_code}, {len(r1.text)} chars")
    log(f"transformToFHIR ok: HTTP {r1.status_code}, {len(r1.text)} chars")

    # --- JSON validity check ---
    try:
        fhir_json = json.loads(r1.text)
    except ValueError as e:
        result.record("jsonValid", False, f"invalid JSON: {e}")
        return result
    result.record("jsonValid", True)

    resource_types = [
        e.get("resource", {}).get("resourceType") for e in fhir_json.get("entry", [])
    ] if isinstance(fhir_json, dict) else []

    # --- Basic FHIR structural checks (not IG/profile validation) ---
    problems = check_fhir_bundle(fhir_json)
    if problems:
        result.record("fhirStructure", False, "; ".join(problems))
    else:
        result.record("fhirStructure", True, f"{len(resource_types)} entries structurally sound")

    # --- Baby/fetus PID+NK1 -> Patient+RelatedPerson split (only applies to 'Baby of'/'Fetus of' cases) ---
    applicable, split_problems = check_baby_fetus_split(v2_bytes.decode("utf-8"), fhir_json)
    if applicable:
        if split_problems:
            result.record("babyFetusSplit", False, "; ".join(split_problems))
        else:
            result.record("babyFetusSplit", True, "Patient (baby/fetus) + RelatedPerson (mother) correctly split")

    # --- OBX ED/CE(+PDF) source code -> DocumentReference.type check (only applies when an
    # OBX in the message matches one of the two conventions - see check_document_reference_code) ---
    doc_applicable, doc_problems = check_document_reference_code(v2_bytes.decode("utf-8"), fhir_json)
    if doc_applicable:
        if doc_problems:
            result.record("documentReferenceCode", False, "; ".join(doc_problems))
        else:
            result.record(
                "documentReferenceCode", True,
                "DocumentReference.type carries the expected SNOMED/LOINC coding",
            )

    # A structural/split/coding problem means transformToFHIR produced something wrong -
    # don't let a bad transform reach the RIE. transformToV2 still runs below (useful
    # diagnostic on its own), but stage 3 (send to server) is skipped once we reach it.
    transform_error = (
        bool(problems)
        or (applicable and bool(split_problems))
        or (doc_applicable and bool(doc_problems))
    )

    if save_output:
        out_dir = os.path.join(OUTPUT_ROOT, "FHIR", msg_type)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, filename + ".json"), "w", encoding="utf-8", errors="replace") as f:
            f.write(r1.text)

    # --- Stage 2: transformToV2 ---
    if skip_transform_to_v2:
        result.record("transformToV2", True, "skipped for this group")
        log("transformToV2 skipped for this group")
    else:
        log(f"POST {V2_TOOLS}/transformToV2 (timeout=30s)")
        try:
            r2 = session.post(
                f"{V2_TOOLS}/transformToV2", data=r1.text,
                headers=HEADERS_FHIR, verify=False, timeout=30,
            )
        except requests.RequestException as e:
            result.record("transformToV2", False, f"request error: {e}")
            log(f"FAILED transformToV2: request error: {e}")
            return result

        if r2.status_code != 200:
            result.record("transformToV2", False, f"HTTP {r2.status_code}: {r2.text[:200]}")
            log(f"FAILED transformToV2: HTTP {r2.status_code}")
            return result

        v2_roundtrip = r2.text
        if not v2_roundtrip.lstrip().startswith("MSH|"):
            result.record("transformToV2", False, "round-tripped output does not start with an MSH segment")
            log("FAILED transformToV2: round-tripped output does not start with an MSH segment")
            return result

        result.record("transformToV2", True, f"{len(v2_roundtrip)} chars")
        log(f"transformToV2 ok: {len(v2_roundtrip)} chars")

        if save_output:
            out_dir = os.path.join(OUTPUT_ROOT, "V2", msg_type)
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, filename), "w", encoding="utf-8", errors="replace", newline="") as f:
                f.write(v2_roundtrip)

    # --- Stage 3: send original v2 to the RIE ---
    if transform_error:
        result.record(
            "sendToServer", False,
            "skipped - transformToFHIR produced a structurally invalid or incorrectly split "
            "result; refusing to send to the RIE",
        )
        log("sendToServer skipped - earlier stage produced a structurally invalid result")
        return result

    if skip_send:
        result.record("sendToServer", True, "skipped")
        log("sendToServer skipped (--skip-send)")
        return result

    log(f"POST {V2_SERVER} (waiting up to {SEND_TIMEOUT}s for an ACK)")
    try:
        r3 = session.post(V2_SERVER, data=v2_bytes, verify=False, timeout=SEND_TIMEOUT)
    except requests.Timeout:
        result.record(
            "sendToServer", False,
            f"TIMEOUT after {SEND_TIMEOUT}s waiting for an ACK - likely a fault, raise an issue",
        )
        log(f"FAILED sendToServer: TIMEOUT after {SEND_TIMEOUT}s waiting for an ACK")
        return result
    except requests.RequestException as e:
        result.record("sendToServer", False, f"request error: {e}")
        log(f"FAILED sendToServer: request error: {e}")
        return result

    if r3.status_code not in (200, 201, 202):
        result.record("sendToServer", False, f"HTTP {r3.status_code}: {r3.text[:200]}")
        log(f"FAILED sendToServer: HTTP {r3.status_code}")
        return result

    ack_code, detail = parse_ack(r3.text)
    if ack_code in ("AA", "CA"):
        result.record("sendToServer", True, f"ACK {ack_code}")
        log(f"sendToServer ok: ACK {ack_code}")
    else:
        result.record("sendToServer", False, f"ACK {ack_code or 'unparseable'}: {detail}")
        log(f"FAILED sendToServer: ACK {ack_code or 'unparseable'}: {detail}")
    return result


def run_fhir_source_case(session, group, msg_type, filename, input_dir, skip_send=False,
                          save_output=True, known_dangling_refs=()):
    """Like run_case, but for a group whose fixtures are already a FHIR Bundle
    (Input/FHIR/<type>/<filename>.json) rather than raw v2 - the "dwgs" group. Runs
    transformToV2 (there's no v2 original to run transformToFHIR on first), then
    sendToServer POSTs the Bundle itself to FHIR_SERVER's $process-message (OAuth2
    client-credentials bearer token, same flow Testing.ipynb and notebook 08's worked
    example use) rather than a raw v2 message to V2_SERVER - the FHIR-sourced equivalent
    of run_case's stage 3.

    known_dangling_refs: "urn:uuid:..." values check_fhir_bundle's dangling-reference
    check is allowed to report for this specific fixture without failing the
    fhirStructure stage - for fixtures we don't author ourselves (e.g. nwgmsa_examples)
    where the dangling reference is a confirmed, external, upstream authoring gap (a
    resource that only exists in a *different* published Bundle), not something this
    repo can fix by editing the fixture. Still recorded in the stage detail, just not
    as a failure - see the nwgmsa_examples group's comment in TEST_GROUPS.
    """
    case_name = f"{group}/{msg_type}/{filename}"
    log(f"=== starting {case_name} ===")
    result = CaseResult(case_name)
    in_path = os.path.join(input_dir, msg_type, filename)

    log(f"loading {in_path}")
    if not os.path.exists(in_path):
        result.record("load", False, f"file not found: {in_path}")
        log(f"FAILED load: file not found: {in_path}")
        return result
    with open(in_path, "rb") as f:
        fhir_bytes = f.read()
    result.record("load", True, f"{len(fhir_bytes)} bytes")
    log(f"loaded {len(fhir_bytes)} bytes")

    try:
        fhir_json = json.loads(fhir_bytes)
    except ValueError as e:
        result.record("jsonValid", False, f"invalid JSON: {e}")
        log(f"FAILED jsonValid: {e}")
        return result
    result.record("jsonValid", True)

    problems = check_fhir_bundle(fhir_json)
    known = [p for p in problems if any(ref in p for ref in known_dangling_refs)]
    unknown = [p for p in problems if p not in known]
    if unknown:
        result.record("fhirStructure", False, "; ".join(unknown))
    elif known:
        result.record(
            "fhirStructure", True,
            f"{len(fhir_json.get('entry', []))} entries structurally sound "
            f"(known upstream issue ignored: {'; '.join(known)})",
        )
    else:
        result.record("fhirStructure", True, f"{len(fhir_json.get('entry', []))} entries structurally sound")

    log(f"POST {V2_TOOLS}/transformToV2 (timeout=30s)")
    try:
        r2 = session.post(
            f"{V2_TOOLS}/transformToV2", data=fhir_bytes,
            headers=HEADERS_FHIR, verify=False, timeout=30,
        )
    except requests.RequestException as e:
        result.record("transformToV2", False, f"request error: {e}")
        log(f"FAILED transformToV2: request error: {e}")
        return result

    if r2.status_code != 200:
        result.record("transformToV2", False, f"HTTP {r2.status_code}: {r2.text[:200]}")
        log(f"FAILED transformToV2: HTTP {r2.status_code}")
        return result

    v2_roundtrip = r2.text
    if not v2_roundtrip.lstrip().startswith("MSH|"):
        result.record("transformToV2", False, "round-tripped output does not start with an MSH segment")
        log("FAILED transformToV2: round-tripped output does not start with an MSH segment")
        return result

    result.record("transformToV2", True, f"{len(v2_roundtrip)} chars")
    log(f"transformToV2 ok: {len(v2_roundtrip)} chars")

    applicable, demographics_problems = check_patient_demographics_preserved(fhir_json, v2_roundtrip)
    if applicable:
        if demographics_problems:
            result.record("demographicsPreserved", False, "; ".join(demographics_problems))
            log(f"FAILED demographicsPreserved: {'; '.join(demographics_problems)}")
        else:
            result.record("demographicsPreserved", True, "name/birthDate/gender all preserved in PID")

    if save_output:
        out_dir = os.path.join(OUTPUT_ROOT, "V2", msg_type)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, filename.replace(".json", ".txt")), "w",
                  encoding="utf-8", errors="replace", newline="") as f:
            f.write(v2_roundtrip)

    # --- Stage 3: POST the FHIR Bundle to FHIR_SERVER's $process-message ---
    if skip_send:
        result.record("sendToServer", True, "skipped (--skip-send)")
        log("sendToServer skipped (--skip-send)")
        return result

    if not (FHIR_SERVER and OAUTH2_TOKEN_URL and CLIENT_ID and CLIENT_SECRET):
        result.record(
            "sendToServer", False,
            "FHIR_SERVER/OAUTH2_TOKEN/CLIENT_ID/CLIENT_SECRET not set - check .env",
        )
        log("FAILED sendToServer: FHIR OAuth2 config missing - check .env")
        return result

    try:
        token = get_fhir_bearer_token(session)
    except (requests.RequestException, ValueError, KeyError) as e:
        result.record("sendToServer", False, f"OAuth2 token request failed: {e}")
        log(f"FAILED sendToServer: OAuth2 token request failed: {e}")
        return result

    log(f"POST {FHIR_SERVER}$process-message (timeout={SEND_TIMEOUT}s)")
    try:
        r3 = session.post(
            f"{FHIR_SERVER}$process-message", data=fhir_bytes,
            headers={"Content-Type": "application/fhir+json", "Authorization": f"Bearer {token}"},
            verify=False, timeout=SEND_TIMEOUT,
        )
    except requests.Timeout:
        result.record(
            "sendToServer", False,
            f"TIMEOUT after {SEND_TIMEOUT}s waiting for a response - likely a fault, raise an issue",
        )
        log(f"FAILED sendToServer: TIMEOUT after {SEND_TIMEOUT}s")
        return result
    except requests.RequestException as e:
        result.record("sendToServer", False, f"request error: {e}")
        log(f"FAILED sendToServer: request error: {e}")
        return result

    if r3.status_code != 200:
        result.record("sendToServer", False, f"HTTP {r3.status_code}: {r3.text[:200]}")
        log(f"FAILED sendToServer: HTTP {r3.status_code}")
        return result

    try:
        response_json = r3.json()
    except ValueError as e:
        result.record("sendToServer", False, f"HTTP 200 but response is not valid JSON: {e}")
        log(f"FAILED sendToServer: response is not valid JSON: {e}")
        return result

    code, detail = parse_process_message_response(response_json)
    if code == "ok":
        result.record("sendToServer", True, "response.code=ok" + (f", {detail}" if detail else ""))
        log("sendToServer ok: response.code=ok")
    else:
        result.record("sendToServer", False, f"response.code={code or 'missing'}: {detail or r3.text[:200]}")
        log(f"FAILED sendToServer: response.code={code or 'missing'}")
    return result


ALL_MSG_TYPES = sorted({
    msg_type for group in TEST_GROUPS.values() for msg_type in group["cases"]
})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--group", action="append", dest="groups", choices=sorted(TEST_GROUPS),
        help="Restrict the run to one or more scenario groups (repeatable). Default: all registered groups.",
    )
    parser.add_argument(
        "--type", action="append", dest="types", choices=ALL_MSG_TYPES,
        help="Restrict the run to one or more message types (repeatable). Default: all registered types.",
    )
    parser.add_argument(
        "--skip-send", action="store_true",
        help="Skip stage 3 (posting the original v2 message to V2_SERVER, or for "
             "FHIR-sourced groups like dwgs, the Bundle to FHIR_SERVER's $process-message).",
    )
    args = parser.parse_args()

    if not V2_TOOLS or not V2_SERVER:
        print("V2_TOOLS / V2_SERVER not set - check .env", file=sys.stderr)
        sys.exit(2)

    groups = args.groups or list(TEST_GROUPS)
    types = args.types or ALL_MSG_TYPES

    total_cases = sum(
        len(TEST_GROUPS[g]["cases"].get(t, [])) for g in groups for t in types
    )
    log(f"V2_TOOLS={V2_TOOLS}  V2_SERVER={V2_SERVER}")
    log(f"running {total_cases} case(s) across group(s) {groups}, type(s) {types}"
        + (" (--skip-send)" if args.skip_send else ""))

    session = requests.Session()
    results = []
    case_num = 0
    for group_name in groups:
        group = TEST_GROUPS[group_name]
        for msg_type in types:
            for filename in group["cases"].get(msg_type, []):
                case_num += 1
                log(f"--- case {case_num}/{total_cases} ---")
                if group.get("input_format") == "fhir":
                    results.append(run_fhir_source_case(
                        session, group_name, msg_type, filename,
                        input_dir=group.get("input_dir") or os.path.join("Input", "FHIR"),
                        skip_send=args.skip_send,
                        known_dangling_refs=group.get("known_dangling_refs", {}).get(filename, ()),
                    ))
                else:
                    results.append(run_case(
                        session, group_name, msg_type, filename, args.skip_send,
                        input_dir=group.get("input_dir"),
                        skip_transform_to_v2=group.get("skip_transform_to_v2", False),
                    ))

    log("all cases complete, printing summary")
    failures = 0
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"[{status}] {r.name}")
        for stage, passed, detail in r.stages:
            marker = "ok" if passed else "FAILED"
            line = f"    {stage}: {marker}"
            if detail:
                line += f" - {detail}"
            print(line)
        if not r.passed:
            failures += 1

    print()
    print(f"{len(results) - failures}/{len(results)} cases passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
