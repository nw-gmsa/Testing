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
external PDS `Patient.link` (also `reference`-only). Both were removed rather than
repaired by adding an `identifier`, since in both cases there wasn't a well-known
identifier system+value on hand to add one correctly - but the underlying rule, for any
future resync hitting the same shape of failure, is to prefer adding a
`Reference.identifier` (an "enterprise identifier" - a real identifier system the
target is actually known by, e.g. an NHS number or ODS code) over deleting the
reference outright, wherever one is available.

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

The other 13 are genomic orders (`Bundle-NonWGS*`, `Bundle-WGSTestOrderForm-Example`,
the two `UKCore-Bundle-MichaelJonesRequest-Example_*`) or a genomic report
(`Bundle-GenomicReportVisibility-JamesWilson-Example`).

## Why conversion was needed

`FHIR_SERVER`'s `$process-message` (the ESB) doesn't accept `Bundle.type` `"transaction"`
— 10 of the 13 order examples are built as a conditional-upload transaction (`entry[]`
each carrying a `request: {method, url}`, no `MessageHeader`), the shape NHS Digital's
own IG uses for direct RESTful submission to a FHIR repository, not for messaging.
`Bundle-GenomicReportVisibility-JamesWilson-Example` is a `"collection"` Bundle with no
`MessageHeader` and no `entry.fullUrl` at all.

Two examples (`UKCore-Bundle-MichaelJonesRequest-Example_minimal`/`_v3_message`) were
already proper `"message"` Bundles with a `MessageHeader` — used as the template for
converting the rest, and copied into place otherwise unconverted (aside from the
eventCoding and Practitioner/Organization fixes below, which applied to these two same
as everything else).

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

For the one report (`Bundle-GenomicReportVisibility-JamesWilson-Example`, a
`"collection"` Bundle with 3 entries and no `fullUrl`s at all):

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
