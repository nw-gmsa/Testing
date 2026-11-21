"""Export the NW-GMSA IG's ExampleScenarios as end-to-end test fixtures.

Reads the IG's SUSHI output (fsh-generated/resources) and, for each ExampleScenario that has
example content, writes Input/Scenarios/<ScenarioId>/:

- FHIR/<event>/NN-<id>.json - each FHIR Message (Bundle type message), under its event code
  (O21, R01, O19, O51, T02), which is where IntegrationTest.py looks for FHIR cases
- FHIR/Document/NN-<id>.json - FHIR Documents
- FHIR/<ResourceType>/NN-<id>.json - any other example resources the scenario names
- README.md - the scenario's steps, with the file for each step

NN is the number of the first step that uses the file.

A scenario can also keep its original HL7 v2 messages in Input/Scenarios/<ScenarioId>/V2/<event>/NN-<name>.txt
(hand-authored, so kept when the scenario is re-exported). When it does, IntegrationTest.py runs the scenario
from the v2 messages - the FHIR is the RIE's conversion of them - and the IG's FHIR Messages are for reference. It also writes Input/Scenarios/scenarios.json,
the manifest IntegrationTest.py reads to build one FHIR test group per scenario.

The IG is the source of truth for these scenarios: re-run this after changing the IG's examples.

Usage:
    python3 Input/Scenarios/export_ig_scenarios.py [path to the IG's fsh-generated/resources]
"""
import json
import os
import shutil
import sys

IG_BASE = "https://nw-gmsa.github.io/en/"
CONTENT_EXT = "http://hl7.org/fhir/5.0/StructureDefinition/extension-ExampleScenario.instance.version.content"
TITLE_EXT = "http://hl7.org/fhir/5.0/StructureDefinition/extension-ExampleScenario.instance.version.title"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def load(resources_dir, filename):
    with open(os.path.join(resources_dir, filename)) as f:
        return json.load(f)


def resource_file(resources_dir, reference):
    """'Bundle/GenomicsOrderMessage-RPX' -> its file: SUSHI output, or the IG's hand-authored input/resources."""
    resource_type, resource_id = reference.split("/", 1)
    name = f"{resource_type}-{resource_id}.json"
    for folder in (resources_dir, os.path.join(resources_dir, "..", "..", "input", "resources")):
        if os.path.exists(os.path.join(folder, name)):
            return os.path.join(folder, name)
    raise FileNotFoundError(f"{reference}: {name} not found in fsh-generated/resources or input/resources")


def scenario_titles(resources_dir):
    ig = next(f for f in os.listdir(resources_dir) if f.startswith("ImplementationGuide-"))
    titles = {}
    for res in load(resources_dir, ig)["definition"]["resource"]:
        ref = res.get("reference", {}).get("reference", "")
        if ref.startswith("ExampleScenario/"):
            titles[ref.split("/", 1)[1]] = res.get("name", ref)
    return titles


def kind_of(resource):
    """Sub-folder for a resource: the event code for a message, Document, or the resource type."""
    if resource["resourceType"] == "Bundle" and resource.get("type") == "message":
        return resource["entry"][0]["resource"]["eventCoding"]["code"]
    if resource["resourceType"] == "Bundle" and resource.get("type") == "document":
        return "Document"
    return resource["resourceType"]


def patients(resource):
    """'Given FAMILY (identifier)' for each Patient in a Bundle."""
    found = []
    for entry in resource.get("entry", []):
        r = entry["resource"]
        if r["resourceType"] == "Patient":
            name = r.get("name", [{}])[0]
            ident = (r.get("identifier") or [{}])[0].get("value", "")
            found.append(f"{' '.join(name.get('given', []))} {name.get('family', '')} ({ident})".strip())
    return found


def export(resources_dir):
    titles = scenario_titles(resources_dir)
    manifest = {}
    for filename in sorted(os.listdir(resources_dir)):
        if not filename.startswith("ExampleScenario-"):
            continue
        scenario = load(resources_dir, filename)
        sid = scenario["id"]
        actors = {a["actorId"]: a.get("name", a["actorId"]) for a in scenario.get("actor", [])}

        # (resourceId, versionId) -> (version title, content reference)
        versions = {}
        for inst in scenario.get("instance", []):
            for ver in inst.get("version", []):
                ext = {e["url"]: e for e in ver.get("extension", [])}
                if CONTENT_EXT in ext:
                    versions[(inst["resourceId"], ver["versionId"])] = (
                        ext.get(TITLE_EXT, {}).get("valueString", ""),
                        ext[CONTENT_EXT]["valueReference"]["reference"])
            # a step that leaves versionId blank means the instance's only version
            if len(inst.get("version", [])) == 1 and (inst["resourceId"], inst["version"][0]["versionId"]) in versions:
                versions[(inst["resourceId"], "")] = versions[(inst["resourceId"], inst["version"][0]["versionId"])]
        if not versions:
            continue  # background scenarios with no example content

        steps, files, step_of = [], {}, {}
        for process in scenario.get("process", []):
            for step in process.get("step", []):
                op = step.get("operation")
                if not op:
                    continue
                request = op.get("request", {})
                key = (request.get("resourceId"), request.get("versionId"))
                ref = versions.get(key, (None, None))[1]
                steps.append((op.get("number", ""), process.get("title", ""), op.get("name", ""),
                              actors.get(op.get("initiator"), op.get("initiator", "")),
                              actors.get(op.get("receiver"), op.get("receiver", "")), ref))
                if ref and ref not in step_of:
                    step_of[ref] = op.get("number", "")
        # content not used by any step (for example the Condition versions) keeps the order it's listed in
        for ref in [v[1] for v in versions.values()]:
            step_of.setdefault(ref, "")

        out = os.path.join(OUT_DIR, sid)
        v2_dir = os.path.join(out, "V2")
        v2_files = {}  # event -> sorted filenames, kept across the re-export
        if os.path.isdir(v2_dir):
            for event in sorted(os.listdir(v2_dir)):
                if os.path.isdir(os.path.join(v2_dir, event)):
                    v2_files[event] = sorted(f for f in os.listdir(os.path.join(v2_dir, event)) if f.endswith(".txt"))
        if os.path.isdir(out):
            for entry in os.listdir(out):
                if entry != "V2":
                    path = os.path.join(out, entry)
                    shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
        cases = {}
        for ref, number in step_of.items():
            with open(resource_file(resources_dir, ref)) as f:
                resource = json.load(f)
            kind = kind_of(resource)
            prefix = f"{int(number):02d}-" if number.isdigit() else ""
            name = f"{prefix}{ref.split('/', 1)[1]}.json"
            os.makedirs(os.path.join(out, "FHIR", kind), exist_ok=True)
            with open(os.path.join(out, "FHIR", kind, name), "w") as f:
                json.dump(resource, f, indent=2)
                f.write("\n")
            files[ref] = (kind, name, resource)
            if resource["resourceType"] == "Bundle" and resource.get("type") == "message":
                cases.setdefault(kind, []).append(name)

        title = titles.get(sid, sid)
        lines = [f"# End-to-end test: {title}", "",
                 f"Test cases for the NW-GMSA IG scenario [{title}]({IG_BASE}ExampleScenario-{sid}.html), "
                 "exported from the IG's examples by `../export_ig_scenarios.py`. Don't edit these files by hand: "
                 "change the IG and re-export.", "",
                 ] + ([
                 "The steps with an HL7 v2 message are run from the original v2 messages under `V2/<event>/` by "
                 f"`IntegrationTest.py` (group `scenario_{sid}`), so the FHIR is the RIE's conversion of them. The v2 "
                 "messages are hand-authored and kept when the scenario is re-exported, and the IG's FHIR Messages for "
                 "those steps are for reference. FHIR Messages for any other steps are run as FHIR (group "
                 f"`scenario_{sid}_fhir`).", ""] if v2_files else [
                 "All the steps are FHIR. FHIR Messages are under `FHIR/<event>/` and are run by `IntegrationTest.py` "
                 f"(group `scenario_{sid}`); FHIR Documents and other resources are for reference.", ""])
        people = sorted({p for _, _, r in files.values() for p in patients(r)})
        if people:
            lines += ["## Patients", ""] + [f"- {p}" for p in people] + [""]
        v2_by_step = {f[:2]: f"`V2/{event}/{f}`" for event, names in v2_files.items() for f in names if f[:2].isdigit()}
        lines += ["## Test cases", ""]
        if v2_files:
            lines += ["| Step | Stage | Interaction | From → To | HL7 v2 | FHIR (IG) |", "|---|---|---|---|---|---|"]
        else:
            lines += ["| Step | Stage | Interaction | From → To | Format | File |", "|---|---|---|---|---|---|"]
        for number, stage, name, initiator, receiver, ref in steps:
            if ref in files:
                kind, fname, resource = files[ref]
                fmt = (f"FHIR Message {kind}" if resource.get("type") == "message"
                       else "FHIR Document" if kind == "Document" else f"FHIR {kind}")
                cell = f"`FHIR/{kind}/{fname}`"
            else:
                fmt, cell = "Not covered", "-"
            if v2_files:
                v2_cell = v2_by_step.get(f"{int(number):02d}" if number.isdigit() else "", "-")
                lines.append(f"| {number} | {stage} | {name} | {initiator} → {receiver} | {v2_cell} | {cell} |")
            else:
                lines.append(f"| {number} | {stage} | {name} | {initiator} → {receiver} | {fmt} | {cell} |")
        unused = [r for r in files if r not in {s[5] for s in steps}]
        if unused:
            lines += ["", "Other example resources in this scenario:", ""]
            lines += [f"- `FHIR/{files[r][0]}/{files[r][1]}`" for r in unused]
        with open(os.path.join(out, "README.md"), "w") as f:
            f.write("\n".join(lines) + "\n")
        manifest[sid] = {"title": title, "cases": cases}
        if v2_files:
            manifest[sid]["v2_cases"] = v2_files
        print(f"{sid}: {len(files)} files, {sum(len(v) for v in cases.values())} messages")

    with open(os.path.join(OUT_DIR, "scenarios.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    default = os.path.join(OUT_DIR, "..", "..", "..", "FHIRGenomics", "fsh-generated", "resources")
    export(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else default))
