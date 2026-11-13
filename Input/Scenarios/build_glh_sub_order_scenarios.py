"""Build the test fixtures for the two GLH to GLH sub-order scenarios in the NW-GMSA IG:

- Rapid Prenatal Exome Sequencing  https://nw-gmsa.github.io/en/ExampleScenario-RapidPrenatalExomeSequencing.html
- Specialist Test for Another GLH  https://nw-gmsa.github.io/en/ExampleScenario-SpecialistTestForAnotherGLH.html

GOMS is simulated: the files under GOMS/ are the FHIR payloads the RIE would post to, or get back
from, the Genomic Order Management Service. The HL7 v2 files under V2/ are the NW side (the Trust
EPR and iGene to and from the RIE). Re-run after changing a constant below:

    python3 Input/Scenarios/build_glh_sub_order_scenarios.py
"""
import base64
import json
import os
import uuid

# North Thames GLH: "LONDON NORTH GENOMIC LABORATORY HUB (GLH)" in the NHS ODS directory (active,
# Great Ormond Street postcode). Check against the GOMS onboarding details.
NORTH_THAMES_GLH_ODS = "69A70"
NORTH_THAMES_GLH_NAME = "North Thames Genomic Laboratory Hub"
# North Thames GLH's report number system is also not yet confirmed.
NORTH_THAMES_REPORT_SYSTEM = "https://fhir.example.nhs.uk/NorthThamesGLH/ReportIdentifier"
# Simulated GOMS base URL. Replace with the GOMS Int environment base URL when connecting to it.
GOMS = "https://goms.simulated.example.nhs.uk/FHIR/R4"
NW_GLH_ODS = "699X0"
NW_GLH_NAME = "NHS North West Genomics"
GOSH_ODS = "RP4"
GOSH_NAME = "Great Ormond Street Hospital for Children NHS Foundation Trust"
MFT_ODS = "R0A"
MFT_NAME = "Manchester University NHS Foundation Trust"

ROOT = os.path.dirname(os.path.abspath(__file__))
NS = uuid.UUID("0f3b6a51-7f0e-4c1e-9d6a-2a6b9e1c0001")

ODS = "https://fhir.nhs.uk/Id/ods-organization-code"
NHS = "https://fhir.nhs.uk/Id/nhs-number"
V2_0203 = "http://terminology.hl7.org/CodeSystem/v2-0203"
GTD = "https://fhir.nhs.uk/CodeSystem/England-GenomicTestDirectory"
SCT = "http://snomed.info/sct"
IGENE_REPORT = "https://fhir.nwgenomics.nhs.uk/iGene/ReportIdentifier"
IGENE_REFERRAL = "https://fhir.nwgenomics.nhs.uk/iGene/ReferralIdentifier"
WORKFLOW = "https://fhir.nwgenomics.nhs.uk/CodeSystem/referral-workflow-status"
REASON = "https://fhir.nwgenomics.nhs.uk/CodeSystem/referral-status-reason"


def urn(name):
    return f"urn:uuid:{uuid.uuid5(NS, name)}"


# ------------------------------------------------------------------------------ HL7 v2
def seg(name, values):
    fields = [name]
    for n, v in values.items():
        while len(fields) <= n:
            fields.append("")
        fields[n] = v
    return "|".join(fields)


def msh(sending_app, sending_fac, receiving_app, receiving_fac, ts, msg_type, control_id):
    return "|".join(["MSH", "^~\\&", sending_app, sending_fac, receiving_app, receiving_fac, ts, "",
                     msg_type, control_id, "T", "2.5.1", "", "", "AL"])


def write_v2(path, segments):
    path = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        fh.write("\r".join(segments) + "\r")
    print("wrote", os.path.relpath(path, ROOT))


def write_json(path, resource):
    path = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(resource, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("wrote", os.path.relpath(path, ROOT))


def pdf(lines):
    """A minimal one-page PDF with the given lines of text (Helvetica), base64 encoded."""
    text = "BT /F1 11 Tf 50 780 Td 14 TL " + " ".join(
        "(" + line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") '" for line in lines) + " ET"
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(text)} >>\nstream\n{text}\nendstream",
    ]
    out, offsets = "%PDF-1.4\n", []
    for n, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{n} 0 obj\n{body}\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n" + "".join(f"{o:010d} 00000 n \n" for o in offsets)
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return base64.b64encode(out.encode("latin-1")).decode()


def mdm_t02(path, control, ts, pid, doc_number, lines):
    """LAB report sent to the central repository (UGR): MDM^T02 with the report as a PDF in OBX-5."""
    write_v2(path, [
        msh("RIE", NW_GLH_ODS, "UGR", "X26", ts, "MDM^T02^MDM_T02", control),
        seg("EVN", {1: "T02", 2: ts}),
        pid,
        seg("PV1", {1: "1", 2: "O"}),
        seg("TXA", {1: "1", 2: "1054161000000101^Genetic report^SCT", 3: "AP", 6: ts, 12: doc_number, 17: "AU"}),
        seg("OBX", {1: "1", 2: "ED", 3: "1054161000000101^Genetic report^SCT", 5: "^application^pdf^Base64^" + pdf(lines), 11: "F"}),
    ])


def org(ods, name):
    return {"identifier": {"system": ODS, "value": ods}, "display": name, "type": "Organization"}


def ident(value, type_code, assigner, system=None):
    i = {"type": {"coding": [{"system": V2_0203, "code": type_code}]}, "value": value,
         "assigner": {"identifier": {"system": ODS, "value": assigner}}}
    if system:
        i["system"] = system
    return i


def task(name, status, business, sr_url, sr_identifier, patient_url, patient_identifier, requester, owner,
         authored, modified, reason=None, output_url=None):
    t = {
        "resourceType": "Task",
        "id": name,
        "status": status,
        "businessStatus": {"coding": [{"system": WORKFLOW, "code": business}]},
        "intent": "order",
        "code": {"coding": [{"system": "http://hl7.org/fhir/CodeSystem/task-code", "code": "fulfill"}]},
        "focus": {"reference": sr_url, "type": "ServiceRequest", "identifier": sr_identifier},
        "for": {"reference": patient_url, "identifier": patient_identifier},
        "authoredOn": authored,
        "lastModified": modified,
        "requester": requester,
        "owner": owner,
    }
    if reason:
        t["statusReason"] = {"coding": [{"system": REASON, "code": reason[0]}], "text": reason[1]}
    if output_url:
        t["output"] = [{"type": {"text": "Laboratory Report"}, "valueReference": {"reference": output_url, "type": "DiagnosticReport"}}]
    return t


def searchset(query, entries):
    return {"resourceType": "Bundle", "type": "searchset", "total": sum(1 for e in entries if e[2] == "match"),
            "link": [{"relation": "self", "url": query}],
            "entry": [{"fullUrl": u, "resource": r, "search": {"mode": m}} for u, r, m in entries]}


def transaction(entries):
    return {"resourceType": "Bundle", "type": "transaction",
            "entry": [{"fullUrl": u, "resource": r, "request": {"method": m, "url": url}} for u, r, m, url in entries]}


def report(name, dr_identifier, based_on, patient_url, patient_identifier, performer, interpreter, code, effective,
           conclusion, outcome):
    return {
        "resourceType": "DiagnosticReport",
        "meta": {"profile": ["https://fhir.nwgenomics.nhs.uk/StructureDefinition/LaboratoryReport"]},
        "id": name,
        "identifier": [dr_identifier],
        "basedOn": [based_on],
        "status": "final",
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0074", "code": "GE"}]}],
        "code": {"coding": [code, {"system": SCT, "code": "1054161000000101", "display": "Genetic report"}]},
        "subject": {"reference": patient_url, "identifier": patient_identifier},
        "effectiveDateTime": effective,
        "issued": effective,
        "performer": [performer],
        "resultsInterpreter": [interpreter],
        "conclusion": conclusion,
        "conclusionCode": [{"coding": [{"system": "https://fhir.nwgenomics.nhs.uk/CodeSystem/GenomicTestOutcomeCode",
                                        "code": outcome[0], "display": outcome[1]}]}],
    }


# ================================================================== Rapid Prenatal Exome Sequencing
A = "RapidPrenatalExomeSequencing"
FETUS_PID = seg("PID", {1: "1", 3: "R0A200080^^^R0A^MR", 5: "LONDON^Fetus of Cersei", 8: "U", 11: "^^^^SE1 2AA"})
FETUS_PID_IGENE = seg("PID", {1: "1", 3: "R0A200080^^^R0A^MR~200080^^^699X0^PI", 5: "LONDON^Fetus of Cersei", 8: "U",
                              11: "^^^^SE1 2AA"})
MOTHER_NK1 = seg("NK1", {1: "1", 2: "LONDON^Cersei", 3: "MTH^Mother^HL70063", 4: "^^^^SE1 2AA", 15: "F", 16: "19731003",
                         33: "9737383230^^^NHS^NH~505181^^^R0A^MR"})
FATHER_NK1 = seg("NK1", {1: "2", 2: "LANCASTER^Jaime", 3: "FTH^Father^HL70063", 15: "M", 16: "19700727",
                         33: "9737383214^^^NHS^NH~2401711^^^R0A^MR"})
FMU = "C9000114^FICTITIOUS^Fiona^^^Dr^^^GMC"
MFT_ORC21 = f"{MFT_NAME}^^{MFT_ODS}^^^ODS"
NW_ORC21 = f"{NW_GLH_NAME}^^{NW_GLH_ODS}^^^ODS"
NT_ORC21 = f"{NORTH_THAMES_GLH_NAME}^^{NORTH_THAMES_GLH_ODS}^^^ODS"
EXOME = "R21^Rapid prenatal exome sequencing^England-GenomicTestDirectory"

write_v2(f"{A}/V2/O21/PRE-01-LAB1-OML_O21-MFT-to-iGene.txt", [
    msh("EPR", MFT_ODS, "IGENE", NW_GLH_ODS, "20260901100000+0100", "OML^O21^OML_O21", "PRE-01-0001"),
    FETUS_PID, MOTHER_NK1, FATHER_NK1,
    seg("PV1", {1: "1", 2: "O", 3: "^^^R0A", 7: FMU}),
    seg("ORC", {1: "NW", 2: "R0A26-77001^R0A", 4: "R0A26-77001^R0A", 9: "20260901100000+0100", 12: FMU, 21: MFT_ORC21}),
    seg("OBR", {1: "1", 2: "R0A26-77001^R0A", 4: "R21.1^Fetal anomalies with a likely genetic cause (Common aneuploidy testing)^England-GenomicTestDirectory", 16: FMU}),
    "NTE|1||Rapid prenatal exome sequencing (trio) to follow if QF-PCR and microarray are negative. Parental bloods sent.",
    seg("DG1", {1: "1", 3: "268805008^Suspected fetal abnormality^SCT"}),
    seg("SPM", {1: "1", 2: "R0A26-S0901&R0A", 4: "119373006^Amniotic fluid specimen^SCT", 17: "20260901090000+0100"}),
    seg("ORC", {1: "NW", 2: "R0A26-77002^R0A", 4: "R0A26-77001^R0A", 9: "20260901100000+0100", 12: FMU, 21: MFT_ORC21}),
    seg("OBR", {1: "2", 2: "R0A26-77002^R0A", 4: "R21.3^Fetal anomalies with a likely genetic cause (Microarray)^England-GenomicTestDirectory", 16: FMU}),
])

write_v2(f"{A}/V2/R01/PRE-02a-LAB3-ORU_R01-iGene-to-MFT-first-line-result.txt", [
    msh("IGENE", NW_GLH_ODS, "EPR", MFT_ODS, "20260903150000+0100", "ORU^R01^ORU_R01", "PRE-02a-0001"),
    FETUS_PID_IGENE, MOTHER_NK1,
    seg("ORC", {1: "RE", 2: "R0A26-77001^R0A", 3: "R26-PX01^699X0", 12: FMU, 21: MFT_ORC21}),
    seg("OBR", {1: "1", 2: "R0A26-77001^R0A", 3: "T26-PX01^699X0", 4: "R21.1^Fetal anomalies with a likely genetic cause (Common aneuploidy testing)^England-GenomicTestDirectory",
                16: FMU, 22: "20260903150000+0100", 25: "F", 32: "CS90002&FICTITIOUS&Priya"}),
    seg("OBX", {1: "1", 2: "CWE", 3: "51968-6^Genetic analysis overall interpretation^LN", 4: "1", 5: "LA6576-8^Positive^LN", 11: "F"}),
    seg("OBX", {1: "2", 2: "TX", 3: "51969-4^Genetic analysis report^LN", 4: "1",
                5: "QF-PCR: result consistent with trisomy 18. Exome sequencing will not go ahead. Fictitious example.", 11: "F"}),
])

SUB_ORDER_ORC = {2: "T26-PX02^699X0", 4: "R26-PX01^699X0", 8: "R0A26-77001&R0A^T26-PX01&699X0"}
write_v2(f"{A}/V2/O21/PRE-03-LAB35-OML_O21-iGene-to-RIE-sub-order.txt", [
    msh("IGENE", NW_GLH_ODS, "GOMS", NORTH_THAMES_GLH_ODS, "20260905100000+0100", "OML^O21^OML_O21", "PRE-03-0001"),
    FETUS_PID_IGENE, MOTHER_NK1, FATHER_NK1,
    seg("ORC", {1: "NW", **SUB_ORDER_ORC, 9: "20260905100000+0100", 12: "ZZ_ELI^FICTITIOUS^Eli^^^^^^699X0", 21: NW_ORC21}),
    seg("OBR", {1: "1", 2: "T26-PX02^699X0", 4: EXOME}),
    "NTE|1||Trio DNA sent: fetal DNA from amniotic fluid, maternal and paternal DNA. QF-PCR and microarray normal.",
    seg("SPM", {1: "1", 2: "S26-PX01&699X0", 4: "258566005^Deoxyribonucleic acid sample^SCT",
                17: "20260901090000+0100", 18: "20260902100000+0100"}),
])

# Simulated GOMS: the RIE converts PRE-03 to a FHIR Transaction and posts it to GOMS
fetus_url, mother_url, father_url = urn("pre-fetus"), urn("pre-mother"), urn("pre-father")
pre_sr_url, pre_task_url, pre_spec_url = urn("pre-sub-order"), urn("pre-task"), urn("pre-specimen")
fetus_identifier = ident("R0A200080", "MR", MFT_ODS)
pre_sr_identifier = ident("T26-PX02", "PLAC", NW_GLH_ODS, IGENE_REPORT)
nw_org, nt_org = org(NW_GLH_ODS, NW_GLH_NAME), org(NORTH_THAMES_GLH_ODS, NORTH_THAMES_GLH_NAME)
fetus = {"resourceType": "Patient", "identifier": [fetus_identifier], "name": [{"use": "temp", "family": "LONDON", "given": ["Fetus of Cersei"]}],
         "gender": "unknown", "address": [{"postalCode": "SE1 2AA"}]}
mother = {"resourceType": "RelatedPerson", "identifier": [{"system": NHS, "value": "9737383230"}],
          "patient": {"reference": fetus_url, "identifier": fetus_identifier},
          "relationship": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "NMTHF", "display": "natural mother of fetus"}]}],
          "name": [{"family": "LONDON", "given": ["Cersei"]}], "gender": "female", "birthDate": "1973-10-03"}
father = {"resourceType": "RelatedPerson", "identifier": [{"system": NHS, "value": "9737383214"}],
          "patient": {"reference": fetus_url, "identifier": fetus_identifier},
          "relationship": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "NFTHF", "display": "natural father of fetus"}]}],
          "name": [{"family": "LANCASTER", "given": ["Jaime"]}], "gender": "male", "birthDate": "1970-07-27"}
pre_specimen = {"resourceType": "Specimen", "identifier": [ident("S26-PX01", "FILL", NW_GLH_ODS)],
                "type": {"coding": [{"system": SCT, "code": "258566005", "display": "Deoxyribonucleic acid sample"}]},
                "subject": {"reference": fetus_url}, "receivedTime": "2026-09-02T10:00:00+01:00",
                "note": [{"text": "Trio DNA: fetal (amniotic fluid), maternal and paternal."}]}
pre_sr = {"resourceType": "ServiceRequest", "identifier": [pre_sr_identifier],
          "basedOn": [{"type": "ServiceRequest", "identifier": ident("R0A26-77001", "PLAC", MFT_ODS)}],
          "requisition": ident("R26-PX01", "PGN", NW_GLH_ODS, IGENE_REFERRAL),
          "status": "active", "intent": "filler-order",
          "category": [{"coding": [{"system": SCT, "code": "116148004", "display": "Molecular genetics procedure"}]}],
          "code": {"coding": [{"system": GTD, "code": "R21", "display": "Rapid prenatal exome sequencing"}]},
          "subject": {"reference": fetus_url, "identifier": fetus_identifier},
          "authoredOn": "2026-09-05T10:00:00+01:00", "requester": nw_org, "performer": [nt_org],
          "reasonCode": [{"coding": [{"system": SCT, "code": "268805008", "display": "Suspected fetal abnormality"}]}],
          "specimen": [{"reference": pre_spec_url}],
          "note": [{"text": "QF-PCR and microarray normal."}]}
pre_task_requested = task("pre-task", "requested", "requested", pre_sr_url, pre_sr_identifier, fetus_url, fetus_identifier,
                          nw_org, nt_org, "2026-09-05T10:00:00+01:00", "2026-09-05T10:00:00+01:00")
write_json(f"{A}/GOMS/PRE-03-GOMS-POST-Transaction-sub-order.json", transaction([
    (fetus_url, fetus, "POST", "Patient"), (mother_url, mother, "POST", "RelatedPerson"),
    (father_url, father, "POST", "RelatedPerson"), (pre_spec_url, pre_specimen, "POST", "Specimen"),
    (pre_sr_url, pre_sr, "POST", "ServiceRequest"), (pre_task_url, {k: v for k, v in pre_task_requested.items() if k != "id"}, "POST", "Task"),
]))

TASK_QUERY_NW = f"{GOMS}/Task?requester:identifier={ODS}|{NW_GLH_ODS}&_lastUpdated=gt2026-09-05"
pre_task_accepted = task("pre-task", "accepted", "accepted", f"ServiceRequest/pre-sub-order", pre_sr_identifier,
                         "Patient/pre-fetus", fetus_identifier, nw_org, nt_org, "2026-09-05T10:00:00+01:00", "2026-09-07T09:00:00+01:00")
write_json(f"{A}/GOMS/PRE-04-GOMS-GET-Task-accepted.json", searchset(TASK_QUERY_NW, [(f"{GOMS}/Task/pre-task", pre_task_accepted, "match")]))
write_v2(f"{A}/V2/O51/PRE-04-OSU_O51-RIE-to-iGene-accepted.txt", [
    msh("RIE", NW_GLH_ODS, "IGENE", NW_GLH_ODS, "20260907090500+0100", "OSU^O51^OSU_O51", "PRE-04-0001"),
    FETUS_PID_IGENE,
    seg("ORC", {1: "OK", 2: "T26-PX02^699X0", 3: f"NT26-000123^{NORTH_THAMES_GLH_ODS}", 5: "IP", 9: "20260907090000+0100", 21: NT_ORC21}),
])

pre_task_declined = task("pre-task", "rejected", "declined", "ServiceRequest/pre-sub-order", pre_sr_identifier,
                         "Patient/pre-fetus", fetus_identifier, nw_org, nt_org, "2026-09-05T10:00:00+01:00", "2026-09-07T09:00:00+01:00",
                         reason=("not-eligible", "Does not meet the R21 rapid prenatal exome sequencing eligibility criteria. Please contact the laboratory."))
write_json(f"{A}/GOMS/PRE-04a-GOMS-GET-Task-declined.json", searchset(TASK_QUERY_NW, [(f"{GOMS}/Task/pre-task", pre_task_declined, "match")]))
write_v2(f"{A}/V2/O51/PRE-04a-OSU_O51-RIE-to-iGene-declined.txt", [
    msh("RIE", NW_GLH_ODS, "IGENE", NW_GLH_ODS, "20260907090500+0100", "OSU^O51^OSU_O51", "PRE-04a-0001"),
    FETUS_PID_IGENE,
    seg("ORC", {1: "UA", 2: "T26-PX02^699X0", 5: "CA", 9: "20260907090000+0100",
                16: "not-eligible^Does not meet the R21 rapid prenatal exome sequencing eligibility criteria. Please contact the laboratory.^L",
                21: NT_ORC21}),
])

pre_dr_url = urn("pre-report")
nt_scientist = {"identifier": {"system": "https://fhir.hl7.org.uk/Id/hcpc-number", "value": "CS90005"}, "display": "FICTITIOUS, Nathaniel"}
pre_report = report("pre-report", ident("NT26-000123", "FILL", NORTH_THAMES_GLH_ODS, NORTH_THAMES_REPORT_SYSTEM),
                    {"reference": "ServiceRequest/pre-sub-order", "type": "ServiceRequest", "identifier": pre_sr_identifier},
                    "Patient/pre-fetus", fetus_identifier, nt_org, nt_scientist,
                    {"system": GTD, "code": "R21", "display": "Rapid prenatal exome sequencing"}, "2026-09-21T16:00:00+01:00",
                    "No pathogenic or likely pathogenic variant identified in the genes analysed. Fictitious example.",
                    ("311", "RESULT CONSISTENT WITH REFERRAL INDICATION"))
pre_task_completed = task("pre-task", "completed", "completed", "ServiceRequest/pre-sub-order", pre_sr_identifier,
                          "Patient/pre-fetus", fetus_identifier, nw_org, nt_org, "2026-09-05T10:00:00+01:00", "2026-09-21T16:00:00+01:00",
                          output_url="DiagnosticReport/pre-report")
write_json(f"{A}/GOMS/PRE-05-GOMS-GET-Task-completed-with-report.json", searchset(
    TASK_QUERY_NW + "&_include=Task:output", [(f"{GOMS}/Task/pre-task", pre_task_completed, "match"),
                                               (f"{GOMS}/DiagnosticReport/pre-report", pre_report, "include")]))
write_v2(f"{A}/V2/R01/PRE-05-LAB36-ORU_R01-RIE-to-iGene.txt", [
    msh("RIE", NW_GLH_ODS, "IGENE", NW_GLH_ODS, "20260921160500+0100", "ORU^R01^ORU_R01", "PRE-05-0001"),
    FETUS_PID_IGENE,
    seg("ORC", {1: "RE", 2: "T26-PX02^699X0", 3: f"NT26-000123^{NORTH_THAMES_GLH_ODS}", 21: NT_ORC21}),
    seg("OBR", {1: "1", 2: "T26-PX02^699X0", 3: f"NT26-000123^{NORTH_THAMES_GLH_ODS}", 4: EXOME,
                22: "20260921160000+0100", 25: "F", 32: "CS90005&FICTITIOUS&Nathaniel"}),
    seg("OBX", {1: "1", 2: "CWE", 3: "51968-6^Genetic analysis overall interpretation^LN", 4: "1",
                5: "311^RESULT CONSISTENT WITH REFERRAL INDICATION^GenomicTestOutcome", 11: "F"}),
    seg("OBX", {1: "2", 2: "TX", 3: "51969-4^Genetic analysis report^LN", 4: "1",
                5: "No pathogenic or likely pathogenic variant identified in the genes analysed. Fictitious example.", 11: "F"}),
])

write_v2(f"{A}/V2/R01/PRE-06-LAB3-ORU_R01-iGene-to-MFT.txt", [
    msh("IGENE", NW_GLH_ODS, "EPR", MFT_ODS, "20260922100000+0100", "ORU^R01^ORU_R01", "PRE-06-0001"),
    FETUS_PID_IGENE, MOTHER_NK1,
    seg("ORC", {1: "RE", 2: "R0A26-77001^R0A", 3: "R26-PX01^699X0", 12: FMU, 21: MFT_ORC21}),
    seg("OBR", {1: "1", 2: "R0A26-77001^R0A", 3: "T26-PX02^699X0", 4: EXOME, 16: FMU,
                22: "20260922100000+0100", 25: "F", 32: "CS90002&FICTITIOUS&Priya"}),
    seg("OBX", {1: "1", 2: "CWE", 3: "51968-6^Genetic analysis overall interpretation^LN", 4: "1",
                5: "311^RESULT CONSISTENT WITH REFERRAL INDICATION^GenomicTestOutcome", 11: "F"}),
    seg("OBX", {1: "2", 2: "TX", 3: "51969-4^Genetic analysis report^LN", 4: "1",
                5: "QF-PCR and microarray normal. Rapid prenatal exome sequencing (North Thames GLH): no pathogenic or likely pathogenic variant identified. Fictitious example.",
                11: "F"}),
])

mdm_t02(f"{A}/V2/T02/PRE-07-MDM_T02-RIE-to-UGR.txt", "PRE-07-0001", "20260922101500+0100", FETUS_PID_IGENE, "T26-PX02^699X0", [
    "NHS North West Genomics - Genomic Laboratory Report",
    "Patient: Fetus of Cersei LONDON (MFT R0A200080). Mother: Cersei LONDON, NHS 973 738 3230",
    "Test: Rapid prenatal exome sequencing (R21), trio. Report T26-PX02",
    "QF-PCR and microarray normal.",
    "Exome sequencing (North Thames GLH): no pathogenic or likely pathogenic variant identified.",
    "Authorised by FICTITIOUS, Priya (HCPC CS90002). Fictitious example.",
])

# ================================================================== Specialist Test for Another GLH
B = "SpecialistTestForAnotherGLH"
WREXHAM_PID = seg("PID", {1: "1", 3: "9737383257^^^NHS^NH~RP43361027^^^RP4^MR", 5: "WREXHAM^Myrcella", 7: "19991013", 8: "F"})
WREXHAM_PID_IGENE = seg("PID", {1: "1", 3: "9737383257^^^NHS^NH~RP43361027^^^RP4^MR~200028^^^699X0^PI", 5: "WREXHAM^Myrcella",
                                7: "19991013", 8: "F"})
GOSH_CLINICIAN = "C9000113^FICTITIOUS^Ottilie^^^Dr^^^GMC"
HEARING = "R67.1^Monogenic hearing loss (WES or Large Panel)^England-GenomicTestDirectory"
patient_url, sr_url, task_url, spec_url = urn("spec-patient"), urn("spec-sub-order"), urn("spec-task"), urn("spec-specimen")
patient_identifier = {"system": NHS, "value": "9737383257"}
sr_identifier = ident("NT26-000456", "PLAC", NORTH_THAMES_GLH_ODS)
patient = {"resourceType": "Patient", "id": "spec-patient",
           "identifier": [{"system": NHS, "value": "9737383257"}, ident("RP43361027", "MR", GOSH_ODS)],
           "name": [{"family": "WREXHAM", "given": ["Myrcella"]}], "gender": "female", "birthDate": "1999-10-13"}
specimen = {"resourceType": "Specimen", "id": "spec-specimen", "identifier": [ident("NT26-S0456", "FILL", NORTH_THAMES_GLH_ODS)],
            "type": {"coding": [{"system": SCT, "code": "258580003", "display": "Whole blood specimen"}]},
            "subject": {"reference": "Patient/spec-patient"}, "collection": {"collectedDateTime": "2026-10-01T09:00:00+01:00"}}
sub_order = {"resourceType": "ServiceRequest", "id": "spec-sub-order", "identifier": [sr_identifier],
             "basedOn": [{"type": "ServiceRequest", "identifier": ident("RP426-1815", "PLAC", GOSH_ODS)}],
             "status": "active", "intent": "filler-order",
             "category": [{"coding": [{"system": SCT, "code": "116148004", "display": "Molecular genetics procedure"}]}],
             "code": {"coding": [{"system": GTD, "code": "R67.1", "display": "Monogenic hearing loss (WES or Large Panel)"}]},
             "subject": {"reference": "Patient/spec-patient", "identifier": patient_identifier},
             "authoredOn": "2026-10-02T10:00:00+01:00", "requester": nt_org, "performer": [nw_org],
             "reasonCode": [{"coding": [{"system": "https://fhir.nwgenomics.nhs.uk/CodeSystem/GenomicClinicalIndication", "code": "R67", "display": "Monogenic hearing loss"}]}],
             "specimen": [{"reference": "Specimen/spec-specimen"}],
             "note": [{"text": f"Ordered by {GOSH_NAME}."}]}
spec_task_requested = task("spec-task", "requested", "requested", "ServiceRequest/spec-sub-order", sr_identifier, "Patient/spec-patient",
                           patient_identifier, nt_org, nw_org, "2026-10-02T10:00:00+01:00", "2026-10-02T10:00:00+01:00")
TASK_QUERY_OWNER = (f"{GOMS}/Task?owner:identifier={ODS}|{NW_GLH_ODS}&status=requested&_include=Task:focus"
                    "&_include:iterate=ServiceRequest:subject&_include:iterate=ServiceRequest:specimen")
write_json(f"{B}/GOMS/SPEC-02-GOMS-GET-Task-requested-with-sub-order.json", searchset(TASK_QUERY_OWNER, [
    (f"{GOMS}/Task/spec-task", spec_task_requested, "match"), (f"{GOMS}/ServiceRequest/spec-sub-order", sub_order, "include"),
    (f"{GOMS}/Patient/spec-patient", patient, "include"), (f"{GOMS}/Specimen/spec-specimen", specimen, "include")]))
write_v2(f"{B}/V2/O21/SPEC-02-LAB35-OML_O21-RIE-to-iGene.txt", [
    msh("RIE", NW_GLH_ODS, "IGENE", NW_GLH_ODS, "20261002101500+0100", "OML^O21^OML_O21", "SPEC-02-0001"),
    WREXHAM_PID,
    seg("ORC", {1: "NW", 2: f"NT26-000456^{NORTH_THAMES_GLH_ODS}", 8: "RP426-1815&RP4", 9: "20261002100000+0100",
                12: GOSH_CLINICIAN, 21: NT_ORC21}),
    seg("OBR", {1: "1", 2: f"NT26-000456^{NORTH_THAMES_GLH_ODS}", 4: HEARING, 16: GOSH_CLINICIAN}),
    f"NTE|1||Ordered by {GOSH_NAME}.",
    seg("SPM", {1: "1", 2: f"NT26-S0456&{NORTH_THAMES_GLH_ODS}", 4: "258580003^Whole blood specimen^SCT", 17: "20261001090000+0100"}),
])


def status_v2(name, control, orc1, orc5, ts, reason=None, filler=True):
    values = {1: orc1, 2: f"NT26-000456^{NORTH_THAMES_GLH_ODS}", 5: orc5, 9: ts, 12: GOSH_CLINICIAN, 21: NW_ORC21}
    if filler:
        values[3] = "R26-HL01^699X0"
    if reason:
        values[16] = reason
    write_v2(f"{B}/V2/O51/{name}", [
        msh("IGENE", NW_GLH_ODS, "GOMS", NORTH_THAMES_GLH_ODS, ts, "OSU^O51^OSU_O51", control), WREXHAM_PID_IGENE, seg("ORC", values)])


def task_update(name, t):
    write_json(f"{B}/GOMS/{name}", transaction([(f"{GOMS}/Task/spec-task", t, "PUT", "Task/spec-task")]))


status_v2("SPEC-03-OSU_O51-iGene-to-RIE-accepted.txt", "SPEC-03-0001", "OK", "IP", "20261005090000+0100")
task_update("SPEC-03-GOMS-PUT-Task-accepted.json", task(
    "spec-task", "accepted", "accepted", "ServiceRequest/spec-sub-order", sr_identifier, "Patient/spec-patient", patient_identifier,
    nt_org, nw_org, "2026-10-02T10:00:00+01:00", "2026-10-05T09:00:00+01:00"))

DECLINE = "Does not meet the R67.1 eligibility criteria. Please contact the laboratory."
status_v2("SPEC-03a-OSU_O51-iGene-to-RIE-declined.txt", "SPEC-03a-0001", "UA", "CA", "20261005090000+0100",
          reason=f"not-eligible^{DECLINE}^L", filler=False)
task_update("SPEC-03a-GOMS-PUT-Task-declined.json", task(
    "spec-task", "rejected", "declined", "ServiceRequest/spec-sub-order", sr_identifier, "Patient/spec-patient", patient_identifier,
    nt_org, nw_org, "2026-10-02T10:00:00+01:00", "2026-10-05T09:00:00+01:00", reason=("not-eligible", DECLINE)))

UNSUITABLE = "Insufficient DNA extracted from the sample. Please send a new blood sample with a new order."
status_v2("SPEC-03b-OSU_O51-iGene-to-RIE-declined-after-acceptance.txt", "SPEC-03b-0001", "UA", "CA", "20261007140000+0100",
          reason=f"sample-unsuitable^{UNSUITABLE}^L")
task_update("SPEC-03b-GOMS-PUT-Task-declined-after-acceptance.json", task(
    "spec-task", "rejected", "declined", "ServiceRequest/spec-sub-order", sr_identifier, "Patient/spec-patient", patient_identifier,
    nt_org, nw_org, "2026-10-02T10:00:00+01:00", "2026-10-07T14:00:00+01:00", reason=("sample-unsuitable", UNSUITABLE)))

nw_scientist = {"identifier": {"system": "https://fhir.hl7.org.uk/Id/hcpc-number", "value": "CS90002"}, "display": "FICTITIOUS, Priya"}
spec_report = report("spec-report", ident("T26-HL01", "FILL", NW_GLH_ODS, IGENE_REPORT),
                     {"reference": "ServiceRequest/spec-sub-order", "type": "ServiceRequest", "identifier": sr_identifier},
                     "Patient/spec-patient", patient_identifier, nw_org, nw_scientist,
                     {"system": GTD, "code": "R67.1", "display": "Monogenic hearing loss (WES or Large Panel)"}, "2026-11-02T15:00:00+00:00",
                     "Compound heterozygous pathogenic variants in GJB2 identified, consistent with the clinical presentation. Fictitious example.",
                     ("321", "VARIANT DETECTED"))
write_v2(f"{B}/V2/R01/SPEC-04-LAB36-ORU_R01-iGene-to-RIE.txt", [
    msh("IGENE", NW_GLH_ODS, "GOMS", NORTH_THAMES_GLH_ODS, "20261102150500+0000", "ORU^R01^ORU_R01", "SPEC-04-0001"),
    WREXHAM_PID_IGENE,
    seg("ORC", {1: "RE", 2: f"NT26-000456^{NORTH_THAMES_GLH_ODS}", 3: "R26-HL01^699X0", 12: GOSH_CLINICIAN, 21: NT_ORC21}),
    seg("OBR", {1: "1", 2: f"NT26-000456^{NORTH_THAMES_GLH_ODS}", 3: "T26-HL01^699X0", 4: HEARING, 16: GOSH_CLINICIAN,
                22: "20261102150000+0000", 25: "F", 32: "CS90002&FICTITIOUS&Priya"}),
    seg("OBX", {1: "1", 2: "CWE", 3: "51968-6^Genetic analysis overall interpretation^LN", 4: "1", 5: "321^VARIANT DETECTED^GenomicTestOutcome", 11: "F"}),
    seg("OBX", {1: "2", 2: "TX", 3: "51969-4^Genetic analysis report^LN", 4: "1",
                5: "Compound heterozygous pathogenic variants in GJB2 identified, consistent with the clinical presentation. Fictitious example.", 11: "F"}),
])
write_json(f"{B}/GOMS/SPEC-04-GOMS-Transaction-Task-completed-with-report.json", transaction([
    (f"{GOMS}/DiagnosticReport/spec-report", spec_report, "PUT", "DiagnosticReport/spec-report"),
    (f"{GOMS}/Task/spec-task", task("spec-task", "completed", "completed", "ServiceRequest/spec-sub-order", sr_identifier, "Patient/spec-patient",
                                   patient_identifier, nt_org, nw_org, "2026-10-02T10:00:00+01:00", "2026-11-02T15:00:00+00:00",
                                   output_url="DiagnosticReport/spec-report"), "PUT", "Task/spec-task"),
]))

mdm_t02(f"{B}/V2/T02/SPEC-06-MDM_T02-RIE-to-UGR.txt", "SPEC-06-0001", "20261102151500+0000", WREXHAM_PID_IGENE, "T26-HL01^699X0", [
    "NHS North West Genomics - Genomic Laboratory Report",
    "Patient: Myrcella WREXHAM, NHS 973 738 3257 (GOSH RP43361027)",
    "Test: Monogenic hearing loss (R67.1), for North Thames GLH. Report T26-HL01",
    "Compound heterozygous pathogenic variants in GJB2 identified, consistent with the clinical presentation.",
    "Authorised by FICTITIOUS, Priya (HCPC CS90002). Fictitious example.",
])
