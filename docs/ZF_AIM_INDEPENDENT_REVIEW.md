# Independent review brief: zebra-finch vocal-exchange candidate

**Draft for a future reviewer. No reviewer has been contacted, no data or code has been acquired, and no analysis has been run. This is not a partnership, protocol approval, or request to interpret calls as human language.**

## Why this candidate

ZF-AIM is a strong literature lead for studying the structure of vocal exchanges: its authors report more than 1,000 hours of zebra-finch vocal interactions and a model that predicts the next caller, call token and wait time. The work is a bioRxiv preprint, and its outcomes concern acoustic timing and contingency rather than decoded semantic meaning. The current [v3 page](https://www.biorxiv.org/content/10.64898/2026.02.12.705387v3) is titled “Leveraging AI-powered interactive playbacks to decipher rules of communication in zebra finches” and states that its title and abstract were updated; this bibliographic note does not change the review's findings or establish translation.

This brief asks whether a bounded, independent reproduction or challenge is scientifically and practically justified. It does not assume that this is the best dataset for every Talk2Nature goal. Great tits remain a separate large song-structure methods path; budgerigars remain a possible phone-study cohort only if access and safeguards are established.

## Evidence and unresolved points

- The preprint's Methods report 834,309 calls from 21 birds across 40 live pair interactions; a Results passage reports 20 birds. The paper describes a pair-based split, but the reviewed text does not establish that evaluation birds are disjoint from training birds.
- The separate [Zenodo data record](https://doi.org/10.5281/zenodo.23047646) lists four raw example recordings and processed archives. Its API license field says CC BY-SA 4.0 while its description says CC BY-NC. The record does not establish that the full analyzed corpus is deposited or which exact files each license statement covers.
- The separate [26.6 GB code/model record](https://zenodo.org/records/23024019) describes code and weights as MIT, but its single ZIP was not inspected. That statement does not establish rights to audio, annotations or other assets inside it.
- No recordings, archives, source code or model weights have been downloaded or run. Provider checksums are not locally verified. The review must not presume that any item is reusable.

## October 29 metadata-only crosswalk and current decision

Fresh, certificate-verified reads of the official Zenodo APIs for [data record 23047646](https://zenodo.org/api/records/23047646) and [code/model record 23024019](https://zenodo.org/api/records/23024019) matched the previously saved complete top-level manifests: 11 data-record files and one code/model ZIP. No payload bytes were requested. The data record's description identifies only four raw example tracks: Pair 27, Pair 3003 (yoked control), Pair 5014 (ZF-AIM) and Pair 5031 (ZF-AIM ablated), with raw audio totaling about 43.5 GB. It also lists processed-data, detector, pipeline and model assets. The metadata does not establish that these examples or the opaque processed archive contain the complete 40-pair, 834,309-call natural-interaction corpus or expose its pair-to-bird map. The API still declares CC BY-SA 4.0 while the same description says CC BY-NC. The release's unchanged inventory and checksums are provider metadata only; no checksum was verified against bytes.

The separate code/model record still lists one 26.6 GB ZIP and a record-level MIT identifier. Its description names a `StreamPlayback/` folder for real-time experiments and `zf_aim_data/` next-call metadata, but neither the archive nor its internal license scope was inspected. The v3 preprint's 34/6 pair split remains pair-level; whole-bird separation is not established, and the paper's 20-versus-21 bird count remains unresolved.

**Decision:** defer ZF-AIM as Talk2Nature's first benchmark and keep it as prior art. The paper already tests interactive AI-driven playback; claiming a first AI bird conversation or incorporating playback would conflict with Talk2Nature's zero-command observation rule. A passive next-caller/timing analysis could be a distinct research question, but the full corpus, bird/session grouping, data rights and independent review are not ready. No media, archive, code or weights were acquired or run; no playback, training, recruitment or external contact occurred. Powdermill's metadata-only gate review now supports an optional schema/pipeline rehearsal, not a generalization benchmark. Continue with the more promising ArcticBirdSounds site-group candidate only if class support, independent sessions, source rights, leakage and qualified review can be established. Keep real-data admission and AutoResearch **NOT READY**.

## Questions for an avian-communication reviewer

1. Is the paper accurately characterized as evidence about response timing and acoustic adaptation, rather than call meaning or human-directed communication?
2. Which biological question, if any, is worth independently reproducing from the described data? What observable outcome and unit of analysis would make it interpretable?
3. What would make a pair-level evaluation relevant to the intended claim? If the claim is generalization to unfamiliar birds, which identities and interaction records must be held out together?
4. What important behavior, social context or alternative explanation is missing from the reported annotations or proposed task?

## Questions for an ML/statistical reviewer

1. What exact record-level manifest is needed to determine whether birds, pairs, sessions or recording conditions cross the reported split?
2. Which baseline must be beaten (for example, call-rate, prior-caller, timing-only or pair/context-only) before an acoustic contribution is credible?
3. Which primary metric and uncertainty calculation respect repeated calls within birds, pairs and sessions? What result would justify stopping rather than trying a more complex model?
4. Is there a defensible locked evaluation set in the released materials? If not, what independent holdout or narrower estimand is necessary?

## Data-scope review

Please identify which claims can be checked from public metadata and which require a maintainer clarification or an unavailable artifact. In particular, assess the exact file-level scope of the conflicting license declarations and whether the deposited files cover the analyzed corpus. A reviewer cannot grant rights on behalf of the rights holder. Until the terms and corpus scope are authoritatively resolved, all ZF-AIM media and model assets remain **metadata-only and not admitted for Talk2Nature use**.

## Decision requested

Choose one and explain the evidence:

- **Proceed to a bounded reproduction design** after named rights, corpus and split checks pass.
- **Narrow the claim** to an estimand supportable by the available independent units.
- **Defer or reject this candidate**, and name the smallest additional evidence that could change the decision.

A partial answer is useful. Please give the manuscript version and sections reviewed, state your expertise and any authorship or recent collaboration with the source authors, and cite specific tables, files or passages. “Cannot assess from public evidence” is an acceptable result. Do not send recordings, participant data, private correspondence or unpublished materials.

To respond, use the repository's [scientific methods review issue template](https://github.com/Metivity/talk2nature/issues/new?template=scientific-review.yml). Submitting an issue is public and does not create a partnership or endorsement. Talk2Nature will not start training or playback from this review alone; rights, protocol, welfare and locked-evaluation gates remain separate.

## Source trail

- James et al. (2026), [“Leveraging AI-powered interactive playbacks to decipher rules of communication in zebra finches,” bioRxiv v3](https://www.biorxiv.org/content/10.64898/2026.02.12.705387v3), reviewed main text and methods; not peer reviewed.
- [ZF-AIM data release, Zenodo record 23047646](https://doi.org/10.5281/zenodo.23047646), record metadata only; license declarations conflict.
- [ZF-AIM code/model release, Zenodo record 23024019](https://zenodo.org/records/23024019), top-level record only; 26.6 GB ZIP not inspected.
- See the project's [source-grounded evidence note](../content/research.json) and [current candidate decision](FIRST_ANIMAL_PLAN.md) for the full review scope and alternatives.
