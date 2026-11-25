# Make the research library easier to use and share

## Question and decision

Can a reader move from a catalog artifact to its research context, and share a focused search without sending a long list of instructions? The existing directory listed 378 resources but lacked related-note links, direct record anchors and restorable search links. This milestone improves use of the existing evidence instead of adding another dataset or model integration.

## Implementation and evidence boundary

Resource cards now link to research notes that cite at least one of the same source IDs. The current catalog connects 372 of 378 records this way. This is a citation-based relationship, not independent corroboration or an assertion that every artifact was read in full. The six records without a matching note receive no invented connection. Review depth, version, rights and acquisition decisions remain unchanged.

Every record has a stable fragment link based on its catalog ID. A deliberate **Copy search link** action includes only the search words, resource type and research-use filter. Opening that link restores those controls. Typing does not update browser history or save to browser storage; this feature makes no network requests. Opening a shared URL naturally requests the public page, so search words in a shared link should be treated as public. The interface explains what the link contains.

Unknown filter values fall back to all records; search text is limited to 160 characters. Copied URLs omit unrelated query parameters and record fragments. Clipboard denial provides a normal link as a fallback. Changing filters clears a stale fallback; a delayed copy is labeled as the previous search if the controls changed while it was pending. The unfiltered HTML and source links remain available without JavaScript, with the existing canonical URL.

## Verification

Node checks cover filter combinations, restoring a shared search, safe URL construction, malformed values, clipboard rejection and a pending-copy race. The generated-site check verifies record anchors, related-note links and existing rights boundaries.

In local Chrome, a shared parrot/dataset URL restored 19 of 378 records. A direct fragment reached the expected card, and its related review opened. The document matched 320px and 390px viewports without horizontal overflow. The Copy control displayed success; the browser automation's separate virtual clipboard could not read the page clipboard, so a native clipboard paste round trip was not established. Fallback and URL-byte behavior are covered by the tests.

This is maintainer browser emulation, not independent usability or physical-phone validation. No third-party files, audio, model weights or new research results were acquired. The benchmark decision and AutoResearch remain **NOT READY**. Next: obtain outside use of the search/review path and assess whether its records answer a real research question before expanding the catalog.
