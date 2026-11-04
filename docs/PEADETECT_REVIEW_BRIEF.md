# Independent review request: a narrow PeaDetect reproduction

**Review state:** Open request in project source. No independent review has been received, and no individual researcher has been contacted.

## Decision question

Would a carefully bounded reproduction of PeaDetect be scientifically useful, and what claim can its published five-fold source-recording split support? This is a five-second Indian-peafowl vocalization presence task. It is a separate candidate from Talk2Nature's leading general ten-second bird-sound-presence question. It does not test communication meaning, caller identity, behavior, receiver response, or field performance.

## What the public sources report

The PeaDetect data article describes 2,950 balanced five-second clips, with 1,475 positive and 1,475 absence examples. It reports two annotators, an ornithologist's review of 590 clips, and five folds that keep clips from an original source recording together. All positives and 1,092 absence clips are attributed to Xeno-Canto; the remaining 383 absence clips are from Freesound. From these counts, a platform-only rule that predicts “present” for Xeno-Canto and “absent” for Freesound would score 1,858/2,950 = 62.98% accuracy on the curated balanced collection. This is an arithmetic diagnostic, not a measured model or baseline.

The article and dataset release have separate rights. The article is CC BY-NC 4.0; the Mendeley v1 landing page declares CC BY 4.0 for the dataset release. Each underlying Xeno-Canto or Freesound recording retains its own terms. Those item-level terms and the exact fold memberships have not been reviewed.

## Questions for reviewers

Reviewers with relevant avian bioacoustics, dataset curation, statistical learning, or benchmark-evaluation experience may answer any subset:

1. Is five-second peafowl-vocalization presence a useful, clearly bounded reproduction task? What narrow inference would be defensible?
2. Does grouping clips by original recording support only a new-source-recording claim? What evidence would be needed to assess overlap by recordist, location, device, date, or collection context?
3. Given the source mix and the 62.98% source-only diagnostic, which source/platform, class-prior, and acoustic baselines should be predeclared? Which primary metric and uncertainty unit would be appropriate?
4. What is the smallest public, rights-respecting artifact or aggregate needed to decide whether the exact folds support that claim? Is any manifest-level inspection necessary before this review decision?
5. What separate field-transfer evaluation would be needed before describing the detector as useful outside this curated collection?

## Scope and safeguards

This request is answerable from the linked public article and versioned landing-page metadata. It does not request downloading or inspecting the dataset archive, source rows, exact fold files, audio, labels, or precise coordinates. It does not authorize file access, license acceptance, data acquisition, training, model execution, or animal-facing playback. Any later manifest-only plan requires a separate rights and privacy review and owner approval. The candidate remains metadata-only; AutoResearch and real-data admission remain **NOT READY**.

Please state which sources and sections you actually reviewed, note relevant authorship or conflicts briefly, and distinguish evidence from inference. Do not attach recordings, raw metadata, personal contact details, unpublished material, or sensitive locations. A review is not an endorsement, partnership, or legal opinion.

## Sources

- [Puvanendran et al., “PeaDetect dataset: Curated audio recordings of Indian peafowl vocalizations for bioacoustic monitoring”](https://pmc.ncbi.nlm.nih.gov/articles/PMC13382432/) — primary data article; targeted methods and data-availability review.
- [PeaDetect dataset, Mendeley Data v1](https://data.mendeley.com/datasets/skryf4tkff/1) — versioned landing-page metadata; no payload inspected.

This is an original Talk2Nature review prompt, not a peer review or independent reproduction.
