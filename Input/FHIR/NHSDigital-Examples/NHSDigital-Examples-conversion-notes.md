# NHS Digital genomics IG examples — conversion notes

Source: https://github.com/NHSDigital/NHSDigital-FHIR-Genomics-ImplementationGuide/tree/main/Bundle
(NHS England's National Genomic Medicine Service order/report model — the IG NW-GMSA's
own model sits underneath). Fetched from that repo's `main` branch.

## General rule: a Reference needs Reference.identifier, not just Reference.reference

`FHIR_SERVER` doesn't support a `Reference` that's a bare URL/relative-id `reference`
with no `Reference.identifier` alongside it - true whether the target is genuinely
external (a real system, e.g. NHS England's PDS API) or just something that fails to
resolve inside the Bundle. This is the rule two separate, unrelated-looking fixes below
both turned out to be instances of: CancerSolidTumor's broken `AdditionalContact`
extensions (`valueReference` was `reference`-only, no `identifier`) and Scenario5's
external PDS `Patient.link` (also `reference`-only). CancerSolidTumor's was removed
outright (no identifier was on hand to add); Scenario5's `Patient.link` was instead
repaired by adding the identifier (see "Scenario5's actual cause" below) - the
underlying rule, for any future resync hitting the same shape of failure, is to prefer
adding a `Reference.identifier` (an "enterprise identifier" - a real identifier system
the target is actually known by, e.g. an NHS number or ODS code) over deleting the
reference outright, wherever one is available. Scenario5's `ServiceRequest.basedOn` and
`Specimen.request` (see "Scenario5's real root cause" at the end of this file) are a
third instance of the same rule where no identifier was available - both removed, same
as CancerSolidTumor's.

## Which examples were included

Not every `Bundle/*.json` in that repo is a genomic order or report. Excluded:

- `Bundle-Searchset-Example` — a `searchset`, no clinical content.
- `Bundle-TransactionResponseError-Example` / `Bundle-TransactionResponseSuccess-Example`
  — these are `$process-message`/transaction *responses*, not messages to send — same
  reasoning as excluding the NW-GMSA IG's `GenomicsOrderMessageReply*` bundles from the
  `nwgmsa_examples` group.
- `Bundle-WGSRoD-Example` — `Consent` + `QuestionnaireResponse` ("Record of Discussion"),
  not an order or report.
- `CommunityCloud-Bundle-Example` — `DocumentReference`/`Specimen`/`Device`/`Procedure`
  tracking data, not an order or report.
- `UKCore-Bundle-MichaelJonesSpecimen-Example` — a bare `Specimen`, referenced by the
  `MichaelJonesRequest` examples rather than a standalone case.
- `Bundle-GenomicReportVisibility-JamesWilson-Example` — NHS Digital's only R01/report
  example. Converted and included for a while (see the detailed conversion steps
  further down, kept here as a record of what was tried) but ultimately dropped from
  `IntegrationTest.py`'s `nhsd_examples` group as not fully formed: a `"collection"`
  Bundle with no `fullUrl`s at all, and too thin a resource set (3 entries) to stand in
  for a genuine genomics report.

The other 12 are genomic orders: `Bundle-NonWGS*`, `Bundle-WGSTestOrderForm-Example`,
the two `UKCore-Bundle-MichaelJonesRequest-Example_*`.

## Why conversion was needed

`FHIR_SERVER`'s `$process-message` (the ESB) doesn't accept `Bundle.type` `"transaction"`
— 10 of the 12 order examples are built as a conditional-upload transaction (`entry[]`
each carrying a `request: {method, url}`, no `MessageHeader`), the shape NHS Digital's
own IG uses for direct RESTful submission to a FHIR repository, not for messaging.
`Bundle-GenomicReportVisibility-JamesWilson-Example` (later dropped - see "Which
examples were included" above) was a `"collection"` Bundle with no `MessageHeader` and
no `entry.fullUrl` at all.

Two examples (`UKCore-Bundle-MichaelJonesRequest-Example_minimal`/`_v3_message`) were
already proper `"message"` Bundles with a `MessageHeader` — used as the template for
converting the rest, and copied into place otherwise unconverted (aside from the
eventCoding and Practitioner/Organization fixes below, which applied to these two same
as everything else).

## Multi-patient family-group orders split into one message per patient

Three of the 11 order examples don't just carry one order — they bundle a whole family
group's *linked* orders into a single FHIR message, each with its own `ServiceRequest`
(and, for the fetuses, `Specimen`):

- `Bundle-NonWGSScenario3-FetusAsProband-Example` — fetus + mother (2 `ServiceRequest`s).
- `Bundle-NonWGSScenario4-ProbandWithMultipleFetus-Example` — two fetuses + mother, the
  mother carrying *two* `ServiceRequest`s of her own (one per fetus's requisition/order
  group) — 4 `ServiceRequest`s across 3 patients.
- `Bundle-NonWGSTestOrderForm-FetalScenario-Example` — fetus + mother + father
  (3 `ServiceRequest`s).

OML^O21 (and this repo's LIMS) model one order per message - the live `transformToV2`
tool converting one of these straight to v2 produces a single message with several
repeated `ORC`/`OBR`/`PID` groups rather than several independent orders, which isn't
how NW Genomics' own LIMS expects to receive family-group referrals (see e.g.
`08-subcontracted-laboratory-order-from-external-glh.ipynb`'s Duo/Trio worked examples,
each sent as its own message). Added `split_message_bundle_by_patient` to
`IntegrationTest.py` to do this split on the FHIR side, before `transformToV2` - not
after:

- Grouping is by **patient**, not by `ServiceRequest` — a patient with more than one
  `ServiceRequest` (Scenario4's mother) still ends up as a single message carrying both,
  rather than being split further into one message per order.
- Each output message carries: the patient's own `ServiceRequest`(s); whatever they
  reference (`requester`, `specimen`, `supportingInfo`, `reasonReference`); and any
  `Specimen`/`Observation`/`RelatedPerson` linked to that patient only via its own
  `.subject`/`.patient` field rather than a `ServiceRequest` reference — needed because
  FetalScenario's two `Specimen`s are both on the mother but referenced by no
  `ServiceRequest.specimen` at all, and Scenario3 has an orphan "Second Trimester
  Anomalies?" `Observation` on the mother that NHS Digital's own source data never wires
  into any `ServiceRequest.supportingInfo` either (an upstream authoring gap, preserved
  rather than silently dropped).
- Some of NHS Digital's own mother references have **no `Patient` resource in the
  Bundle at all** — `subject` carries an NHS number `identifier` with no matching
  `Patient` entry (relying on PDS, the same "reference by identifier" pattern applied to
  `Practitioner`/`Organization` elsewhere). Grouping keys on the resolved `Patient`
  fullUrl when one exists, falling back to the raw `Reference.reference` string (both
  the mother's `ServiceRequest.subject` and the Scenario3 orphan `Observation.subject`
  use the identical relative reference, so they still land in the same group) rather
  than treating every such reference as unrelated.
- The combined source files were **replaced** by their per-patient outputs (not kept
  alongside them) — `IntegrationTest.py`'s `nhsd_examples` group now lists
  `Bundle-NonWGSScenario3-FetusAsProband-Example-{FetusA,Mother}.json`,
  `Bundle-NonWGSScenario4-ProbandWithMultipleFetus-Example-{FetusA,FetusB,Mother}.json`,
  and `Bundle-NonWGSTestOrderForm-FetalScenario-Example-{Fetus,Mother,Father}.json` (8
  files, up from the original 3) — every one confirmed live, both `transformToV2` and
  `sendToServer` (8/8 `check_fhir_bundle`-clean, 200 OK, `response.code=ok`).

## Scenario3/Scenario4's mother: a RelatedPerson standing in for a Patient

The `-Mother` split of both Scenario3 and Scenario4 had a real, correctly-formed NHS
number (`9449308322`) - but only ever as a `RelatedPerson.identifier`, never as a
`Patient`. NHS Digital's own source data represents the mother purely via a
`RelatedPerson` resource attached to the **fetus's** record (`RelatedPerson.patient` =
the fetus, `relationship` = `NMTHF` "natural mother of fetus") - correct usage for that
purpose (it survives untouched in the `-FetusA`/`-FetusB` splits, feeding their `NK1`
segments). But the mother's *own* `ServiceRequest` (her own order, in her own split
message) pointed its `subject` at `Patient/51008c44-551e-4272-a2a8-36f7d5363c9c` - an id
with no matching `Patient` entry anywhere in the source Bundle - and her
`supportingInfo` list even referenced the `RelatedPerson` resource directly, as if a
description of her relationship to the fetus were "information supporting" her own
order. Same dangling id reused by **7 different `Observation.subject`s** too - `Patient/
51008c44-...` appeared 8 times in Scenario3's `-Mother` split and 9 times in Scenario4's
(2 `ServiceRequest.subject`s there, one per fetus's order group) - none of them caught
by `check_fhir_bundle`'s dangling-reference check, since that only inspects `urn:uuid:`
references, not relative `ResourceType/id` ones. This looks like NHS Digital example
authoring shorthand specific to this file pair, not a pattern seen anywhere else in the
13 files - no other example's own subject is missing a `Patient` resource while a
`RelatedPerson` carrying the identical identifier sits elsewhere in the same Bundle.

Fixed in both `-Mother` splits: added a real `Patient` entry (identifier-only - no
name/DOB is available anywhere in the source data, so none is invented), rewrote every
`Patient/51008c44-...` reference (`ServiceRequest.subject` and all 7
`Observation.subject`s) to the new Patient's `urn:uuid:` fullUrl, and removed the
`RelatedPerson` entry plus its `supportingInfo` reference from the mother's own message
- a `RelatedPerson` describing "this order's subject in relation to a different
patient" isn't supporting information about her own order once she has her own `Patient`
identity as its `subject`. Confirmed live: both `-Mother` files convert and send clean
(`check_fhir_bundle` OK, 200 OK, `response.code=ok`), `nhsd_examples` still 17/17.

**Open query, raised to NHS England**: `Bundle-NonWGSScenario3-FetusAsProband-Example-Mother.json`
doesn't appear to follow the Genomic Order Management Service IG as published - this is
the "FetusAsProband" scenario, yet this split's own `ServiceRequest.subject` is the
*mother*, not the fetus. A query on this has been raised with NHS England; nothing
further changed here pending their response - the fix above (giving the mother a real
`Patient` resource) stands regardless of how that query resolves, since it was needed
either way to stop the dangling reference, but the deeper "should this order's subject
really be the mother in a fetus-as-proband scenario" question is still open.

## Missing MessageHeader.destination / ServiceRequest.performer

`UKCore-Bundle-MichaelJonesRequest-Example_minimal` had neither
`MessageHeader.destination` nor `ServiceRequest.performer` at all (its `_v3_message`
sibling and every converted order do) - `transformToV2` 500'd on it consistently.
General rule for a future resync hitting the same gap: assume NW Genomics is both the
`MessageHeader.destination` and `ServiceRequest.performer`, using the same
identifier/display pair the conversion already uses everywhere else -
`{"identifier": {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value":
"699X0"}, "display": "NORTH WEST GLH LED BY MANCHESTER UNIVERSITY NHS FOUNDATION
TRUST"}` (wrapped in `destination[0].receiver`/`endpoint: "https://api.service.nhs.uk/
GMS"` for `MessageHeader`, a bare `performer[0]` entry for `ServiceRequest`) - not a
claim that NW Genomics is the "real" destination/performer NHS Digital's example
intended, just this repo's standing assumption (matching every other converted example's
fixed `699X0` destination, see above) applied consistently to whatever's missing.

## What the conversion does — deliberately "basic"

For the 10 transaction-shaped orders:

1. `Bundle.type`: `"transaction"` → `"message"`.
2. Drop `entry[].request` (transaction-only, meaningless on a message Bundle).
3. Add `Bundle.identifier` (a fresh `urn:ietf:rfc:4122` UUID) and `Bundle.timestamp`
   (existing IG examples don't set these; message Bundles require them).
4. Prepend a `MessageHeader` entry:
   - `eventCoding` — `http://terminology.hl7.org/CodeSystem/v2-0003#O21`, matching
     every other order message this repo sends. An earlier version of this conversion
     used NHS Digital's own local `genomictestrequest` code
     (`CodeSystem-Genomics-message-events.json`) instead - `FHIR_SERVER` doesn't
     recognise that CodeSystem, so it's v2-0003 O21 here too, same as everything else.
   - `destination` — fixed at NW Genomics, ODS `699X0`, `endpoint`
     `https://api.service.nhs.uk/GMS` (copied from the `MichaelJonesRequest` template) —
     this is where `FHIR_SERVER` in this repo's `.env` actually routes everything
     regardless of an example's "real" intended GLH; not a claim that `699X0` is the
     clinically correct destination for every scenario here.
   - `sender` — best-effort: the first `ServiceRequest.requester`, resolved to a
     `PractitionerRole.organization` identifier/display already present in that same
     Bundle. Omitted entirely (not left as an empty object) where no such data exists —
     `Bundle-NonWGSTestOrderFormUpdated-FetalScenario-Example` is a 2-entry partial
     "update" fixture (`ServiceRequest` + `Specimen` only) with no `PractitionerRole` of
     its own, so it has no `sender`.
   - `source.endpoint` — a generic placeholder, `https://example.org/fhir/SendingSystem`.
   - `focus` — every `ServiceRequest` entry's own existing `fullUrl` (several of the
     multi-fetus/trio scenarios carry more than one).

Existing `fullUrl`s and internal references are **untouched** otherwise — most of these
examples use absolute placeholder URLs (`http://example.org/fhir/<Type>/<id>`) or
relative (`"<Type>/<id>"`) references rather than `urn:uuid:`, which
`IntegrationTest.py`'s `check_fhir_bundle` dangling-reference check doesn't inspect
(only `urn:uuid:` references are checked), so leaving them as-is doesn't trip it.

For the one report (`Bundle-GenomicReportVisibility-JamesWilson-Example`, later dropped
from `IntegrationTest.py`'s `nhsd_examples` group as not fully formed - see "Which
examples were included" above; kept here as a record of the conversion attempted while
it was still included), a `"collection"` Bundle with 3 entries and no `fullUrl`s at all:

1. `Bundle.type`: `"collection"` → `"message"`.
2. Minted a fresh `urn:uuid:` `fullUrl` per entry (`check_fhir_bundle` requires every
   non-`MessageHeader` entry to have one) — existing relative `"Patient/<id>"`-style
   references inside the resources were left unchanged for the same reason as above.
3. Added `Bundle.identifier`/`Bundle.timestamp`.
4. Prepended a `MessageHeader` with `eventCoding`
   `http://terminology.hl7.org/CodeSystem/v2-0003#R01`, `focus` on the
   `DiagnosticReport`, and the same fixed `699X0` destination. `sender` is set to
   `699X0`/NW Genomics itself (the reporting lab) since this minimal 3-resource example
   carries no referrer-organisation data to extract a more specific sender from.

None of this is a claim that the converted Bundles are clinically or profile-correct for
NHS Digital's own IG — only that they're valid enough, structurally, to exercise this
repo's `transformToV2`/`$process-message` round trip the same way `nwgmsa_examples` and
`dwgs` do.

## Patient.link -> RelatedPerson entries removed

Two examples' `Patient.link` arrays carried a `seealso` link to a `RelatedPerson` entry
in the same Bundle (`Bundle-NonWGSTestOrderForm-FetalScenario-Example`'s two Patients,
`Bundle-NonWGSScenario5-ProductsofConception-Example`'s one) - removed (the link array
entry only, not the `RelatedPerson` resource itself, which is still in the Bundle).
Other `Patient.link` entries (e.g. `seealso` to a PDS `Patient` record) were left alone.
Note: this alone did not resolve `Bundle-NonWGSScenario5-ProductsofConception-Example`'s
`sendToServer` HTTP 422 ("The custom error module does not recognize this error") - see
the Procedure removal below, which was the actual fix for that one.

## Procedure resources converted to Observation

`Bundle-NonWGSScenario{3,4,5}-FetusAsProband/ProbandWithMultipleFetus/
ProductsofConception-Example` and `Bundle-NonWGSTestOrderForm-FetalScenario-Example`
each carried one `Procedure` entry (all four the same fact: SNOMED `52637005` "In vitro
fertilisation", `status` `completed`, a `performedDateTime`, and a
`note` - "Woman's own egg"), referenced only from `ServiceRequest.supportingInfo[]`
(two `ServiceRequest`s in the multi-fetus Scenario4 case). An earlier version of this
conversion removed the `Procedure` entry and its `supportingInfo` reference outright;
this repo doesn't use `Procedure` in the genomic order context (unlike `Observation`,
already used throughout NW-GMSA's own examples for "ask at order" answers), so instead
each is now carried as an `Observation` at the same `fullUrl` (or the same `id` under an
`.../Observation/` URL, for the three using absolute placeholder `fullUrl`s rather than
`urn:uuid:`) - `status: "final"`, `code`/`subject`/`note` copied as-is,
`performedDateTime` renamed to `effectiveDateTime` - with `supportingInfo` re-pointed at
it (`{"reference": ..., "type": "Observation"}`) rather than removed.

## Condition: converted only when referenced from ServiceRequest.supportingInfo

`Condition` itself is a resource type `FHIR_SERVER` accepts - the amended rule is about
*where* it's referenced from, not the resource type: a `Condition` referenced from
`ServiceRequest.reasonReference` is kept as-is (that's what `reasonReference` is for);
one referenced from `ServiceRequest.supportingInfo` is converted to `Observation` the
same way `Procedure` was (`status: "final"`, `code`/`subject`/`note` copied as-is,
`fullUrl`/reference repointed). Every `Condition` across all 13 examples happens to be
referenced from `supportingInfo` only (`Bundle-NonWGSTestOrderForm-Reanalysis-Example`,
`-CancerSolidTumor-Example`, `-QRPatientExtensions-Example`,
`Bundle-WGSTestOrderForm-Example`, `Bundle-NonWGSTestOrderForm-Example`) - none use
`reasonReference` - so in practice all of them convert; the rule stays
reference-site-based rather than blanket, for whenever an example using
`reasonReference` shows up in a future resync.

Before converting, a missing `Condition.subject.reference` is filled in by matching
`subject.identifier` against every `Patient` entry already in the bundle (same
system+value) and pointing `reference` at whichever one matches. This only fired for
`Bundle-NonWGSTestOrderFormQRPatientExtensions-Example`'s two `Condition`s - and found
nothing, because that bundle has no `Patient` entry at all (every resource in it,
`ServiceRequest`/`Observation`/`Specimen` included, is identifier-only); left as-is,
since there's genuinely nothing in the bundle to point at.

## Two more failures traced to bad Patient references, not resource types

`Bundle-NonWGSScenario5-ProductsofConception-Example` and
`Bundle-NonWGSTestOrderForm-CancerSolidTumor-Example` both kept failing `sendToServer`
with the same generic HTTP 422 ("The custom error module does not recognize this
error") through every fix above - the actual cause in each turned out to be a broken
reference to the `Patient`, not an unsupported resource type:

- **Scenario5**: `ServiceRequest.supportingInfo` included an entry with `type:
  "Patient"`, referencing the fetus `Patient` directly - `supportingInfo` is for
  *supporting* resources (`Observation`, `Condition`, `DocumentReference`, etc.), not a
  second `Patient`; no other example does this. The fetus is already properly linked via
  `RelatedPerson.patient` and its own `Specimen`/`Observation`s, so this entry was just
  removed rather than replaced with anything.
- **CancerSolidTumor**: `Condition-LungTumor-Example.subject.identifier.value` was
  `"944930555"` - 9 digits, a truncated/mistyped NHS number - while every other
  reference to the same patient in the bundle correctly uses the 10-digit
  `"9449307555"`. Corrected to match - a real fix, but not what was still failing
  `sendToServer` afterward (see below).

## CancerSolidTumor's actual remaining cause: an external Observation reference

Still 422ing after the NHS number fix above - the actual remaining cause:
`ServiceRequest.supportingInfo`'s reference to `Condition-LungTumor-Example` (converted
to `Observation` above, keeping its original absolute placeholder
`fullUrl`/`http://example.org/fhir/Observation/Condition-LungTumor-Example`) resolved
to something `FHIR_SERVER` treats as external/unknown rather than the Bundle-local
entry sharing that URL. Note this isn't a blanket "absolute URLs never resolve"
rule - `Bundle-NonWGSTestOrderForm-Reanalysis-Example` and `Bundle-WGSTestOrderForm-
Example` reference an `Observation` by the exact same absolute-URL pattern
(`http://example.org/fhir/Observation/Condition-MonogenicHearingLoss-Example`) and pass
fine, so something specific to *this* reference/entry is what tripped it, not the
scheme in general. Removed the `Observation` entry and the `supportingInfo` reference
to it, and added a `ServiceRequest.note` recording that an unknown external
`Observation` reference was removed, rather than silently dropping the content.

## CancerSolidTumor, second bug: a dangling AdditionalContact extension

Still 422ing after the above. `ServiceRequest.extension` carried two
`Extension-UKCore-AdditionalContact` entries, each `valueReference`-ing a
`PractitionerRole` by bare relative reference (no `identifier` fallback, unlike every
other reference in this conversion). One resolved fine
(`PractitionerRole-AnnaLaneKingstonPathology-Example`, present in the bundle); the
other pointed at `PractitionerRole/PractitionerRole-JamesTaylor-Example` - not present;
the bundle's actual entry is `PractitionerRole-JamesTaylorKingstonPathology-Example`
(same "-KingstonPathology-Example" suffix every other `PractitionerRole` id in this file
has, just missing here) - a source-data typo. Removed both
`Extension-UKCore-AdditionalContact` entries rather than fix just the broken one, since
neither carries anything this repo's transform/profile needs (`Coverage`, the third
extension on this `ServiceRequest`, was left alone).

## ServiceRequest.note: recombined multi-entry notes into one

`Annotation.text` (what `ServiceRequest.note[]` holds) supports markdown, including
newlines, within a single string - it isn't meant to be split one sentence per array
entry. 10 of the 13 examples' `ServiceRequest`s did exactly that (e.g. `"Samples are to
be provided at a later date"`, `"No family history of relevant testing"`, and a longer
free-text paragraph as three separate `note` entries, each really one continuous
free-text block from the source data). Recombined every `ServiceRequest` with more than
one `note` entry into a single entry, joining the original entries' `text` values with
`\n`, in their original order (including `CancerSolidTumor`'s own added "Unknown
external Observation reference removed" note from above, now combined with its
existing note into one).

## Scenario5's actual cause: an external PDS Patient reference

Still 422ing after every fix above (the stray `Patient`-typed `supportingInfo` entry
removed earlier was real but not sufficient). Root cause: `Patient.link[0].other`
referenced `https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/
Patient/9449308322` - a `seealso` link out to NHS England's real PDS API, not a
Bundle-local resource, and `reference`-only (see the general rule above). Unique to
this example - no other one of the 13 has a PDS `seealso` link at all. Fixed per that
rule rather than deleted: the URL's own trailing path segment, `9449308322`, is exactly
this same `Patient`'s own NHS number (already `Patient.identifier[0]` in the same
resource) - so `other` now carries `{"identifier": {"system":
"https://fhir.nhs.uk/Id/nhs-number", "value": "9449308322"}, "type": "Patient"}`
instead of the bare external `reference`, preserving the `seealso` link's intent
without a `ServiceRequest.note` needed (nothing was actually removed).

## Practitioner/Organization literal references normalised to identifier-only

`UKCore-Bundle-MichaelJonesRequest-Example_v3_message` was the only example (of all 13)
carrying standalone `Practitioner`/`Organization` resources, referenced by literal
`reference` (`urn:uuid:...`) from `MessageHeader.sender`, `Patient.generalPractitioner`/
`.managingOrganization`, `ServiceRequest.identifier.assigner`/`.performer`,
`PractitionerRole.practitioner`/`.organization`, `Specimen.collection.collector`/
`.container.identifier.assigner`, and `Consent.identifier.assigner`/`.organization`.
None of NW-GMSA's own published examples (`nwgmsa_examples`) ever include a standalone
`Practitioner`/`Organization` resource - every one of those references is
identifier-only (`{"identifier": {...}, "display": "..."}`, no `reference`), matching
this file's own `PractitionerRole` example (`Bundle-GenomicsOrderMessageCodedEntries`).
Converted every one of those 11 literal references the same way (using the target
resource's own `identifier[0]`/name as the `display`) and removed the now-orphaned 3
`Practitioner` + 3 `Organization` entries.

## Scenario5's real root cause: two more `reference`-only external links

Still 422ing after every fix above, including the PDS `Patient.link` fix - the actual
remaining cause was two more instances of the same general rule (see the top of this
file), both on the primary `ServiceRequest`/`Specimen` pair rather than on `Patient`:

- `ServiceRequest.basedOn[0].reference` = `"ServieRequest/ServiceRequest-
  NonWGSTestOrderForm-UsingStoredSample-Example"` - a reference to a prior order this
  Bundle doesn't include (and misspells the resource type as `ServieRequest` besides),
  `reference`-only with no `identifier`.
- `Specimen.request[0].reference` = the same target, same shape.

Confirmed live: removing `ServiceRequest.basedOn` alone took `sendToServer` from
`HTTP 422` to `response.code=ok`. Both were removed (no identifier for
"an order this repo has never seen" was available to add instead) and a note recording
the removal added to `ServiceRequest.note`/`Specimen.note` respectively, per the same
convention used for CancerSolidTumor's external `Observation` reference above. With
both removed, `nhsd_examples` passes 12/12 live.

## Missing Patient/RelatedPerson identity: a placeholder name, not a blank one

Two more gaps, found by counting how many of the 18 files had no `Patient` resource at
all: `Bundle-NonWGSTestOrderFormQRPatientExtensions-Example` (subject is
identifier-only NHS number `9449307873`, no `Patient` anywhere - 10 different
`.subject`/`.patient` fields across the Bundle share that identifier) and
`Bundle-NonWGSTestOrderFormUpdated-FetalScenario-Example` (subject/specimen `.subject`
both `reference`-and-`identifier`, pointing at `Patient/Patient-RyanneBoulderPartner-
Example` - an id with no matching entry, the 2-entry partial "update" fixture missing
even its own father). Both are legitimate "person known only by identifier, relying on
PDS" cases per the general rule - the fix isn't to remove the reference (there's a real
identifier to resolve on), it's to add the missing `Patient`.

Added an identifier-only `Patient` (or, for `RelatedPerson`s in the same situation - see
below - `name`/`gender` added to the existing resource) with `name.family`/`name.given`
both set to the literal string **`"TO BE RESOLVED VIA PDS"`** and `gender: "unknown"` -
a placeholder that's honestly a placeholder (not a fabricated real-looking name), for
every field a v2 `PID-5`/`NK1` name component would otherwise render blank. Wired every
matching `.subject`/`.patient` reference to the new `Patient`'s fullUrl. One
reference-matching subtlety worth recording: the live `transformToV2` tool resolves
`Reference.reference` by **exact fullUrl match only** - not the fullUrl-or-id-suffix
fallback this repo's own `_resolve_bundle_reference`/notebook `find_entry` helpers use.
`Updated-FetalScenario`'s existing relative reference (`"Patient/Patient-RyanneBoulder
Partner-Example"`) needed rewriting to the new Patient's exact `http://example.org/fhir/
Patient/...` fullUrl before the live tool would actually pick up the new name - adding
the `Patient` entry alone wasn't enough. Confirmed live: `PID-5` on both files went from
blank to `TO BE RESOLVED VIA PDS^TO BE RESOLVED VIA PDS^^^^^L`.

Same treatment applied to `RelatedPerson` resources carrying only an NHS number
`identifier` and a `relationship` coding, no `name` - five of them, all `NMTHF`
"natural mother of fetus": Scenario3-FetusA and Scenario4-FetusA/FetusB (the shared
`6473db02-.../86c36eee-...` mother-of-fetus records) and FetalScenario-Fetus/-Mother
(`RelatedPerson-RyanneBoulder-Example`, the mother's own record, duplicated by
`split_message_bundle_by_patient` into both her own message and the fetus's). Not
touched: the three `RelatedPerson`s identified only by a *local* OID (Scenario5's
`NCHILD` record, FetalScenario's father-of-fetus records) rather than an NHS number -
out of scope for this pass, since "known only by NHS number, relying on PDS" is the
specific rule here, not "known only by any identifier." Confirmed live: Scenario3-
FetusA's `NK1-2` (name, previously blank) now reads `TO BE RESOLVED VIA PDS^TO BE
RESOLVED VIA PDS`, ahead of `NK1-3`'s existing `NMTHF^natural mother of fetus^...`
relationship coding. `nhsd_examples` still 17/17 after every one of these changes.

`check_patient_demographics_preserved` (`IntegrationTest.py`) makes the audit behind
this section repeatable: for the primary subject's `Patient`, compares
`name`/`birthDate`/`gender` against the live `transformToV2` output's `PID-5`/`-7`/`-8`,
flagging anything present in FHIR that went missing in v2. Wired into
`run_fhir_source_case` as a `demographicsPreserved` stage (non-fatal - like
`fhirStructure`, recorded but doesn't block `sendToServer`) for every group sourced from
FHIR (`dwgs`, `nwgmsa_examples`, `nhsd_examples`). Not applicable (and silently skipped)
where the subject doesn't resolve to a real `Patient` resource at all, or that `Patient`
has no name/DOB/gender to lose in the first place - both real states, not failures.

## Placeholder identities upgraded to real ones via NHS Digital's own Patient/ folder

The "`TO BE RESOLVED VIA PDS`" placeholders above were a deliberately honest stand-in
for "we don't know, and would ask PDS" - but in practice, a real RGL integration
*would* be able to resolve some of these, and so, it turns out, can this repo: NHS
Digital's IG publishes a
[`Patient/`](https://github.com/NHSDigital/NHSDigital-FHIR-Genomics-ImplementationGuide/tree/main/Patient)
folder of named example patients, keyed by NHS number, separately from the order/report
Bundles that reference them only by identifier. Checked every placeholder's NHS number
against it:

- **QRPatientExtensions' subject** (NHS `9449307873`) - two different published
  `Patient`s share this NHS number in the IG's own test data
  (`Patient-MeirLieberman-Example` and `Patient-PatrickSammy-Example`), so identifier
  alone doesn't disambiguate. Resolved by cross-referencing the *order* content instead:
  `Bundle-NonWGSTestOrderForm-Example` (this file's non-QuestionnaireResponse sibling)
  already carries the same NHS number, the same `GT488`/`TP439` test/reason codes, and
  the same `RGT01` (Addenbrooke's) requester - clearly the same underlying scenario -
  and its own embedded `Patient` is "Meir Anah Lieberman", born 2005-12-19, no `.gender`
  populated (only a `BirthSex` extension, not carried across here either, matching that
  sibling). Replaced the placeholder with the real name/DOB and dropped the placeholder
  `gender: "unknown"` to match. Confirmed live: `PID-5`/`PID-7` now read
  `Lieberman^Meir^Anah`/`20051219`.
- **Updated-FetalScenario's father** (local ID `P-RWT13521`) - the published
  `Patient-RyanneBoulderPartner-Example` genuinely has no `name` either (nothing to
  upgrade there - the placeholder name would have been wrong to invent regardless), but
  *does* specify `gender: "male"`, not `"unknown"`. Corrected the gender; left the name
  absent, matching upstream honestly rather than keeping a placeholder for something now
  confirmed unknowable from this source. Confirmed live: `PID-8` now reads `M`.
- **FetalScenario-Fetus/-Mother's mother-of-fetus `RelatedPerson`** (NHS `9449307687`)
  - this is Ryanne Boulder, whose real `name`/`gender` were already sitting one file
  away as her own committed `Patient` resource (`Bundle-NonWGSTestOrderForm-
  FetalScenario-Example-Mother.json`), and confirmed against the IG's published
  `Patient-RyanneBoulder-Example` too. Replaced the placeholder `RelatedPerson.name`
  with `Ryanne`/`Boulder` and `gender: "unknown"` with `"female"` (her `BirthSex`
  extension) in both files. Confirmed live: FetalScenario-Fetus's `NK1-2` now reads
  `Boulder^Ryanne` (previously the placeholder).
- **Scenario3/Scenario4's mother** (NHS `9449308322`) - checked against every file in
  the IG's `Patient/` folder; no match. Genuinely unresolvable from this source - the
  `TO BE RESOLVED VIA PDS` placeholder (on both her own `Patient` and the two
  `6473db02-.../86c36eee-...` `RelatedPerson` records) stays as the honest answer.

`nhsd_examples` still 17/17 live after every one of these corrections.
