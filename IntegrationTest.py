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
  2. POST that Bundle to {V2_TOOLS}/transformToV2 -> expect a valid v2 (MSH-led) message back
  3. POST the *original* raw v2 message to {V2_SERVER} (the RIE), simulating a real feed;
     expect an ACK within SEND_TIMEOUT seconds with MSA-1 of AA/CA (a slow or negative ACK
     is treated as a fault worth raising, not something to silently wait out).
     Skipped (recorded as failed) if stage 1's structural or baby/fetus-split checks found a
     problem - a message transformToFHIR got wrong isn't sent on to the RIE.

Stage 1/2 outputs are saved under Output/FHIR/<messageType>/ and Output/V2/<messageType>/,
matching the layout produced by Testing.ipynb.

TEST_CASES currently covers the baby/fetus O21 orders and R01 reports; extend it with
further message types/files as they're added.

Usage:
    python3 IntegrationTest.py [--skip-send] [--type O21] [--type R01]

Exit code is 0 if every stage of every case passed, 1 otherwise.
"""

import argparse
import json
import os
import sys

import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

V2_TOOLS = os.getenv("V2_TOOLS")
V2_SERVER = os.getenv("V2_SERVER")

HEADERS_V2 = {"Content-Type": "x-application/hl7-v2+er7"}
HEADERS_FHIR = {"Content-Type": "application/fhir+json"}

# A slow ACK from the RIE is treated as a fault worth flagging, not something to wait out
# indefinitely - see stage 3 below.
SEND_TIMEOUT = 60

# Registry of test cases: message type -> list of filenames under Input/V2/<type>/.
# Extend this as more examples come online.
TEST_CASES = {
    "O21": [
        "OML_O21_QE1_BabyOfLysa_R318.1.txt",
        "OML_O21_RXR_BabyOfGilly_R318.1.txt",
        "OML_O21_UNK_FetusOfYara_R22.1.txt",
        "OML_O21_R0A_FetusOfCersei_R22.1.txt",
    ],
    "R01": [
        "ORU_R01_QE1_BabyOfLysa_R318.1.txt",
        "ORU_R01_RXR_BabyOfGilly_R318.1.txt",
        "ORU_R01_UNK_FetusOfYara_R22.1.txt",
        "ORU_R01_R0A_FetusOfCersei_R22.1.txt",
    ],
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


class CaseResult:
    def __init__(self, name):
        self.name = name
        self.stages = []  # list of (stage_name, passed, detail)

    def record(self, stage, passed, detail=""):
        self.stages.append((stage, passed, detail))

    @property
    def passed(self):
        return all(passed for _, passed, _ in self.stages)


def run_case(session, msg_type, filename, skip_send, save_output=True):
    result = CaseResult(f"{msg_type}/{filename}")
    in_path = os.path.join("Input", "V2", msg_type, filename)

    if not os.path.exists(in_path):
        result.record("load", False, f"file not found: {in_path}")
        return result
    with open(in_path, "rb") as f:
        v2_bytes = f.read()
    result.record("load", True, f"{len(v2_bytes)} bytes")

    # --- Stage 1: transformToFHIR ---
    try:
        r1 = session.post(
            f"{V2_TOOLS}/transformToFHIR", data=v2_bytes,
            headers=HEADERS_V2, verify=False, timeout=30,
        )
    except requests.RequestException as e:
        result.record("transformToFHIR", False, f"request error: {e}")
        return result

    if r1.status_code != 200:
        result.record("transformToFHIR", False, f"HTTP {r1.status_code}: {r1.text[:200]}")
        return result

    result.record("transformToFHIR", True, f"HTTP {r1.status_code}, {len(r1.text)} chars")

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

    # A structural/split problem means transformToFHIR produced something wrong - don't let a
    # bad transform reach the RIE. transformToV2 still runs below (useful diagnostic on its
    # own), but stage 3 (send to server) is skipped once we reach it.
    transform_error = bool(problems) or (applicable and bool(split_problems))

    if save_output:
        out_dir = os.path.join("Output", "FHIR", msg_type)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, filename + ".json"), "w", encoding="utf-8", errors="replace") as f:
            f.write(r1.text)

    # --- Stage 2: transformToV2 ---
    try:
        r2 = session.post(
            f"{V2_TOOLS}/transformToV2", data=r1.text,
            headers=HEADERS_FHIR, verify=False, timeout=30,
        )
    except requests.RequestException as e:
        result.record("transformToV2", False, f"request error: {e}")
        return result

    if r2.status_code != 200:
        result.record("transformToV2", False, f"HTTP {r2.status_code}: {r2.text[:200]}")
        return result

    v2_roundtrip = r2.text
    if not v2_roundtrip.lstrip().startswith("MSH|"):
        result.record("transformToV2", False, "round-tripped output does not start with an MSH segment")
        return result

    result.record("transformToV2", True, f"{len(v2_roundtrip)} chars")

    if save_output:
        out_dir = os.path.join("Output", "V2", msg_type)
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
        return result

    if skip_send:
        result.record("sendToServer", True, "skipped")
        return result

    try:
        r3 = session.post(V2_SERVER, data=v2_bytes, verify=False, timeout=SEND_TIMEOUT)
    except requests.Timeout:
        result.record(
            "sendToServer", False,
            f"TIMEOUT after {SEND_TIMEOUT}s waiting for an ACK - likely a fault, raise an issue",
        )
        return result
    except requests.RequestException as e:
        result.record("sendToServer", False, f"request error: {e}")
        return result

    if r3.status_code not in (200, 201, 202):
        result.record("sendToServer", False, f"HTTP {r3.status_code}: {r3.text[:200]}")
        return result

    ack_code, detail = parse_ack(r3.text)
    if ack_code in ("AA", "CA"):
        result.record("sendToServer", True, f"ACK {ack_code}")
    else:
        result.record("sendToServer", False, f"ACK {ack_code or 'unparseable'}: {detail}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--type", action="append", dest="types", choices=sorted(TEST_CASES),
        help="Restrict the run to one or more message types (repeatable). Default: all registered types.",
    )
    parser.add_argument(
        "--skip-send", action="store_true",
        help="Skip stage 3 (posting the original v2 message to V2_SERVER).",
    )
    args = parser.parse_args()

    if not V2_TOOLS or not V2_SERVER:
        print("V2_TOOLS / V2_SERVER not set - check .env", file=sys.stderr)
        sys.exit(2)

    types = args.types or list(TEST_CASES)

    session = requests.Session()
    results = []
    for msg_type in types:
        for filename in TEST_CASES[msg_type]:
            results.append(run_case(session, msg_type, filename, args.skip_send))

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
