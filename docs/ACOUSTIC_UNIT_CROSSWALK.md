# Acoustic-unit outputs and human observation intervals

**Status:** synthetic schema comparison only. No model, animal recording, human label file, or dataset was loaded. This document does not define a production model-output schema or authorize data admission.

## Why this comparison exists

The TweetyBERT paper is relevant to a future acoustic-structure tool, but its results need a different record type from Talk2Nature's `talk2nature.annotation.v1`. The existing annotation file holds time intervals entered by a person, with a sound-kind field, an optional independently observed context, context provenance, confidence, and notes. TweetyBERT's central inference artifact is a time-indexed latent representation; the paper analyzes those representations with clustering and post-processing. Its masked-spectrogram reconstruction prediction is discarded after training. A latent cluster ID is therefore a model-derived grouping, not an observer's event label or a biological category.

## What the paper actually produces and evaluates

Vengrovski et al. report a 2.7 ms spectrogram time-bin resolution and 2.7 s input windows. At inference they extract latent representations from the multi-head attention layer of the third transformer block. They then use HDBSCAN for exploratory clustering, followed by temporal smoothing; their analyses also replace most outlier bins with the nearest neighboring cluster. The paper evaluates clustering against human syllable/phrase annotations with frame error rate and V-measure. These are paper-specific analyses; they are not an exported Talk2Nature-compatible event file.

The reported split holds out whole songs while the same birds are represented in training and evaluation. This supports a within-known-bird song-level result, not unseen-individual, household, species, or setting generalization. The study is about canary song structure; it does not test call meaning or receiver comprehension. See the [peer-reviewed paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13083638/) and its [DOI](https://doi.org/10.1016/j.patter.2025.101491).

## Field-by-field boundary

| Information | Human annotation (`talk2nature.annotation.v1`) | Model-derived acoustic proposal | Safe relationship |
| --- | --- | --- | --- |
| Time | `start_seconds`, `end_seconds` on a human-marked event | Frame indices tied to an exact hop, sample rate, crop origin and preprocessing; a contiguous run may be displayed as an interval | Show overlap in a separate comparison view. Never replace or silently rewrite human timing. |
| Sound kind | Human-entered `uncertain`, `vocalization` or `other sound` | No sound-kind value unless a separately specified, evaluated classifier predicts one | A cluster or embedding is not a vocalization label. |
| Context | Bounded label plus `context_source` | No behavior/context field in a unit-clustering artifact | Preserve independent observation as its own record; never infer context from cluster identity. |
| Confidence | Human confidence about the marked event | Model score or cluster membership, if a method actually emits it, with named method and calibration status | Do not translate model confidence into human confidence. |
| Identity / grouping | Recording, session and individual identifiers, possibly unknown | Exact model/checkpoint, code/config, input, crop/frame indices and run lineage | Unknown identifiers stay unknown; song-level grouping does not imply held-out animal independence. |
| Cluster | Not part of the current human annotation vocabulary | Nominal, run-local cluster ID or explicit unassigned/outlier state | IDs have no stable meaning across runs unless alignment is independently established. |

Before converting frame indices into seconds, a real implementation would need to retain the sample rate, hop in samples (or an exact rational timebase), crop origin, padding, chunk boundaries and any overlap aggregation rule. The display interval is derived from those values; it should not replace the source frame assignments. The synthetic fixture below intentionally uses a coarse 0.5-second frame hop for readable arithmetic. It does **not** reproduce TweetyBERT's 2.7 ms analysis or its model output.

## Invented fixture

[`examples/acoustic-units.synthetic.json`](../examples/acoustic-units.synthetic.json) contains two separate things: a reference to the existing invented annotation fixture and a made-up run-length sequence. In the invented sequence, cluster `unit-A` overlaps each of the two synthetic `other sound` intervals. This is only a timestamp crosswalk. It does not show that the two tones share a natural vocal unit, that any animal produced them, or that a cluster describes context or meaning. Unassigned frames are not evidence of silence or absence.

The fixture test checks its declared synthetic provenance, valid frame lattice, in-bounds runs and separation from context/meaning labels. It does not validate a model, estimate accuracy, or admit an evaluation dataset.

## Evaluation gates before any real-data experiment

1. A qualified bioacoustics reviewer defines the unit being annotated and whether onset/offset agreement or category agreement answers the actual research question.
2. Preserve the exact human annotation version and source. Measure boundary agreement separately from cluster/category agreement; use a stated tolerance and report missed, extra, merged and split intervals.
3. If clusters are compared with human categories, report permutation-invariant agreement such as V-measure alongside class support and per-class errors. Do not name a cluster by the nearest human label without an explicit alignment method and review.
4. Freeze song/session/individual grouping and preprocessing before evaluation. Keep animals represented in training separate from any claim about unseen animals; use site/device/condition holdouts only when the target generalization requires them.
5. Verify data, code, checkpoint and article terms independently. The TweetyBERT paper's article license does not establish rights for its linked recording payload, code repository or weights.

No benchmark was selected or run here. The article, dataset and code remain separate rights/provenance decisions. AutoResearch and real-data admission remain **NOT READY**.
