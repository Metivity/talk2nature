# ArcticBirdSounds reviewer brief

**State:** internal draft for a future independent review; not sent to anyone.
**Decision requested:** is there a scientifically useful, rights-compatible, site-held-out detection study here, and what is the minimum safe aggregate audit needed to decide?

## Proposed bounded question

Can a passive acoustic model detect annotated bird-vocalization events at a site not used for training, using this corpus and a genuinely site-held-out evaluation?

This would test acoustic event detection/generalization only. It would not test caller identity, behavior, call meaning, a response to a person, or “translation.” The app remains zero-command: no playback, mimicry, prompts, or animal-directed output.

## Why this candidate merits review

The paper describes 20 hours of annotated Arctic recordings from 2018–2019, 15 plots, six locations, and 12,933 temporal annotations in 49 sound classes. Its Data S1 documents filename and deployment metadata; the official OSF record declares CC BY 4.0 for the dataset. [Primary paper](https://doi.org/10.1002/ecy.4047) · [OSF record](https://doi.org/10.17605/OSF.IO/B9TRX).

Our current metadata-only audit found a complete filename-to-site mapping for 2,280 annotation/FLAC pairs across six sites, 19 plot/year groups, and 228 five-minute timestamp groups. A separate uncompressed-WAV directory has 1,600 files mapped to five sites; 680 annotation/FLAC keys have no matching uncompressed WAV filename. The archive central directory showed 2,280 schema-valid CSV/FLAC pairs and two CSV-named entries outside the documented filename schema. No audio bytes, annotation rows, coordinates, model weights, or embeddings were opened or retained.

Several source totals still conflict: the paper and supplement narrative give six and seven locations respectively; the deployment table has six; the paper reports 20 plot/year groups and 2,400 segments, while the complete CSV/FLAC filename manifests account for 19 groups and 2,280 pairs. The audit does not resolve those discrepancies.

## Main validity and rights gates

1. **Class support by site is unknown.** The filename audit does not reveal whether a proposed class is represented well enough across independent training and test sites. Do not inspect or summarize annotation rows until a qualified reviewer scopes the minimum justified aggregate crosswalk and confirms it is compatible with the source terms.
2. **Independent units are not established.** A plot/year or five-minute group may not be the right independence unit. A reviewer should determine how deployments, plots, dates, recorders, and any adjacent clips relate, and which grouping blocks leakage.
3. **Published comparisons are not clean held-out baselines.** ECOGEN selected five ArcticBirdSounds classes and used a 75/25 class-level sample split; its published counts differ by one between Methods and Table 1 (4,318 versus 4,319). The article does not establish a site-held-out evaluation. [ECOGEN primary paper](https://doi.org/10.1111/2041-210X.14239).
4. **Known pretraining overlap matters.** ArcticSoundsNET used approximately 18 hours from ArcticBirdSounds to train its binary BirdNET detector. That detector is not an independent comparator for this corpus. [ArcticSoundsNET primary paper](https://doi.org/10.1016/j.ecoinf.2025.103270).
5. **Component rights remain separate.** The dataset record declares CC BY 4.0 and the linked preparation-code repository declares MIT, but article/supplement rights, model licenses, upstream pretraining data, and any future redistribution or commercial rights need their own review. The present audit authorizes no payload reuse.

## Questions for an independent reviewer

- Is event detection across held-out sites a worthwhile first task, given the amount and structure of this corpus?
- What is the minimum aggregate class-by-site and class-by-deployment summary needed to assess feasibility without exposing labels, precise locations, or unnecessary file identifiers?
- What defines an independent group here: site, deployment, plot/year, date, recorder, or a nested combination?
- How should the 20-versus-19 plot/year and 2,400-versus-2,280 segment discrepancies be reconciled before a frozen split is defined?
- What baseline and primary metric are appropriate under class imbalance, and what minimum support should cause a class or site to be excluded?
- Which pre-trained models, if any, have sufficiently transparent training provenance to be considered without ArcticBirdSounds overlap?
- What results and uncertainty would be scientifically useful, and what stopping rule should prevent an underpowered or misleading benchmark?

## Hold points and next action

Until independent review answers these questions, keep the corpus metadata-only and do not inspect annotation rows, acquire audio, run a model, train, or admit it to AutoResearch. Do not publish a benchmark claim from manifest completeness alone.

After a qualified reviewer is identified through an authorized process, use only the reviewer-approved aggregate crosswalk. Freeze the task, grouping, split, baseline, metrics, exclusions, rights record, and stop criteria before any model execution. If those conditions cannot be met, document a deferral and keep working with synthetic pipeline fixtures.

## Evidence provenance

This brief summarizes the locally recorded audit in `research/arcticbirdsounds_metadata_report.json`, `research/arcticbirdsounds_archive_directory_report.json`, the ArcticBirdSounds entry in `content/research.json`, and the linked primary publications. It adds no new payload inspection and is not an independent scientific review.
