# Independent review brief: zebra-finch vocal clustering

**Draft for a future reviewer. No reviewer has been contacted. No dataset, code or model was downloaded or run, and no Talk2Nature experiment has been performed. This is not a claim that zebra-finch calls have been decoded.**

## Why this study is useful

Lee et al. compare expert manual clustering, automated acoustic clustering and human refinement of model suggestions for zebra-finch vocalizations. The narrow engineering question is useful to Talk2Nature: can a simple review interface help people organize similar-sounding clips while keeping corrections and uncertainty visible?

The paper reports 1,454 vocalizations from three isolated birds and three expert annotations per bird. Mean adjusted Rand index / normalized mutual information were 0.78 / 0.83 for expert-to-expert manual agreement, 0.73 / 0.81 for semi-automated clustering and 0.62 / 0.71 for automated clustering. It reports about 90 minutes per bird for manual clustering and 45 minutes for proofreading semi-automated clusters. These are the authors' results; Talk2Nature has not reproduced them.

## What the study does not establish

- The 80/20 split holds out vocalizations within each bird-and-annotator combination. It does not test transfer to a new bird or species.
- Labels describe acoustic similarity, not validated call types, behavioral meaning, receiver response or a conversation with an animal.
- The dataset's paper-cited v1 and later v2 are separate record DOIs in one Zenodo concept series. A same-title record 18100613 has a distinct concept ID. Their exact archive relationships and source-audio permissions remain unresolved.
- The dataset API declares CC BY 4.0. That metadata does not resolve rights to underlying third-party source audio. The paper acknowledges permission to use a subset of an external dataset.
- The pinned tool repository declares MIT. Its full dependency and model-asset lineage was not audited. The WhisperSeg model page displays Apache-2.0 while the pinned API license value is null; the paper's separate Whisper embedding revision is unidentified.

All article, dataset, software and weight records remain metadata-only in the Talk2Nature resource catalog. Their licenses are evaluated separately. No archive contents were inspected.

## Questions for an avian bioacoustics reviewer

1. Is acoustic clustering a useful first task for community-contributed zebra-finch recordings, or would a different observable label be more valuable?
2. What independent animal, session or context labels would be needed before studying call function or receiver response?
3. Does the paper's small isolated-bird sample fit the proposed annotation-use case, and which biological limitations should be more prominent?

## Questions for an ML / statistics / human-factors reviewer

1. Does the reported comparison justify model suggestions as a review aid, given the within-bird split and three-bird sample?
2. Which whole-bird or whole-session holdout would test transfer to unfamiliar animals?
3. Which baseline, primary agreement measure and uncertainty estimate should govern a small evaluation?
4. How should a beginner interface offer accept, split, merge, uncertain and skip actions without turning suggestions into ground-truth labels?

## Decision requested

Recommend **proceed to a bounded design**, **narrow the question**, or **defer/reject this candidate**. State which source sections you reviewed, your relevant expertise, the most important alternative explanation and the smallest check that could change the recommendation. “Cannot assess from the public record” is useful.

Do not attach recordings, private annotations, participant data, personal information, unpublished material or sensitive wildlife locations to a public review. A review is not an endorsement or partnership. No download, training, playback, model integration or funding claim follows from this brief.

## Source trail

- Lee et al. (2026), [Benchmarking Automated and Semi-Automated Vocal Clustering Methods](https://doi.org/10.3390/app16020810), full article text reviewed; no result reproduced.
- [Zenodo v1 record 18156254](https://zenodo.org/records/18156254) and [v2 record 22657329](https://zenodo.org/records/22657329), metadata only; source-audio scope unresolved.
- [Separate same-title record 18100613](https://zenodo.org/records/18100613), a distinct Zenodo concept; relationship unresolved.
- [Pinned clustering code](https://github.com/hwiora/semi_automated_clustering/tree/5b6f8f0a9783546532e3a2bef76ad12930a2eb56), MIT declared by repository; not executed.
- [Pinned WhisperSeg model card](https://huggingface.co/nccratliri/whisperseg-base-animal-vad-ct2/tree/9f873b8a37fe37eb7543de092d308950ceb96fc0), license metadata conflict remains unresolved.

Submit a public response with the repository's [scientific methods review issue template](https://github.com/Metivity/talk2nature/issues/new?template=scientific-review.yml). Public issues should contain literature critique only, never recordings or private research material.
