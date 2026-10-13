# Biodiversity-data interoperability decision

Reviewed October 13, 2026. This is a standards assessment, not an implemented export or a conformance claim.

## Decision

Keep the current Talk2Nature journals and annotation formats as the source records. Treat the official [Darwin Core Data Package guide](https://dwc.tdwg.org/dp/) as a candidate package format for future structured biodiversity releases and [Audubon Core](https://ac.tdwg.org/termlist/) as a candidate vocabulary for describing media. Do not rename fields and claim compatibility: no Talk2Nature mapping has been validated, and the documentation's reuse license was not established in this review.

The Darwin Core guide issued May 26, 2026, requires a versioned profile, a datapackage.json, at least one data table and explicit table schemas. The current guide recommends Data Package specification v1. It also requires each table field descriptor to come from the official schema for that table; field names cannot be guessed or merely made to look familiar. The conceptual model distinguishes an Organism, an Occurrence, an Identification and a Media entity. Audubon Core describes biodiversity-related multimedia resources; its terms include resource rights, access points and media hashes. The standards address exchange and description. They do not define animal communication meaning, study consent, participant governance or whether a label is scientifically valid.

The guide links to its versioned profile and table-schema index on `rs.tdwg.org`. Requests to those exact published paths returned HTTP 404 from the available environment. The official [TDWG rs.tdwg.org repository](https://github.com/tdwg/rs.tdwg.org/tree/e0cc2509953eeed24ad312b6e91e7bfcadd37a3b/dwc-dp) does contain a profile and table schemas, but the profile and `event` schema trace to commit `e0cc2509953eeed24ad312b6e91e7bfcadd37a3b`, titled “Initial pre-review DwC-DP schemas.” These unversioned files are not treated as the released 1.0 artifacts or a conformance basis. This is a deployment/version mismatch observed in the available sources, not proof that the standards host is generally unavailable.

The official [issue #759](https://github.com/tdwg/dwc/issues/759) is now closed (June 25, 2026); its visible discussion says guide section 3.4 already specifies the field-descriptor rule. The public-review index still listed it as open, so that index is stale. Closure of the discussion does not establish that the versioned profile and schema URLs resolve or that the unversioned pre-review snapshot is the release. See the [guide's normative schema requirements](https://dwc.tdwg.org/dp/).

## Mapping boundary

| Talk2Nature record | Possible standards question | Guardrail |
| --- | --- | --- |
| Station session | Could a reviewed study define a bounded survey/event table? | The app session is currently an operational capture session, not a defined sampling event. Its device clock is explicitly unverified and the public browser tool does not capture location. Do not export it as a scientific `Event` until a protocol defines the event and its time/location basis. |
| WAV or retained clip | Could a media table use Audubon Core descriptions and access metadata? | Keep each recording's rights, checksum, access and withdrawal state separate. A checksum does not establish permission or identity. |
| Energy-detector sound candidate | Is this an instrument record, a media region, or another local event type? | Do not turn a threshold candidate into an organism occurrence, species identification or behavior label by default. |
| Human marker, review or setting note | How should observer-entered evidence and its provenance be represented? | Preserve who/what supplied it, uncertainty and relative time. Do not convert free-text notes into a biological assertion. |
| Animal context selected by the observer | Can an independently reviewed identification be represented separately from the sound file? | The current context control is observer-declared and does not establish species identification or an organism occurrence. |

This boundary preserves the project's distinctions among media, detected candidates, human observations and biological interpretations. The existing AOEF adapter is a separate annotation-workbench bridge; it is not a Darwin Core or Audubon Core implementation.

## Acceptance gate for a future adapter

Do not implement a production export yet. Before describing any future export as compatible or compliant:

1. Define a real study question and protocol that says what one sampling event means, who records it, and how time, location, effort and observer provenance are established.
2. Retrieve and pin the exact official versioned profile and per-table schemas; use their field descriptors directly. Recheck the official schema issue tracker and record the retrieved version or the access failure.
3. Build a fixture from synthetic Station and Listen records only. Keep observed sound/media, detected candidates, human notes and expert-reviewed identification in separate evidence layers.
4. Map only fields with a documented semantic equivalent; preserve unknowns, provenance, permissions, checksums and omitted-field reasons. Never emit an organism occurrence from a detector candidate or observer-selected species context alone.
5. Validate the complete package with an appropriate profile-aware validator and independently review schema, semantics and information loss.
6. Verify export remains local and does not disclose private notes or sensitive locations; publish the mapping, schema/validator versions, synthetic fixture, expected output and limitations together.

Next decision: establish the event definition and obtain the exact released, versioned schemas before drafting a synthetic mapping. Do not substitute the pre-review repository snapshot. Until those gates pass, keep Talk2Nature's own journal format, and do not label it a Darwin Core or Audubon Core export. This assessment adds no production adapter, data release or conformance claim. The source-linked note and separate rights records are in the [research library](../content/research.json) and [resource catalog](../research/resources.json).
