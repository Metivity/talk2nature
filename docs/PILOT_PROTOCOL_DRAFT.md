# First parrot pilot: readiness and observation draft

October 3, 2026. Talk2Nature. Proposed feasibility protocol, not an approved study or an invitation to recruit. Species choice remains provisional; see [FIRST_ANIMAL_PLAN.md](FIRST_ANIMAL_PLAN.md).

## Question and practical sequence

Can two independent reviewers consistently label a few visible behaviors in ordinary, permitted observations of one parrot species? Only after that succeeds should we test whether audio adds useful information on held-out households. A conversational model is not the first deliverable.

1. Confirm which existing carers and species are accessible. Prefer one budgerigar cohort; use cockatiels instead if access and a specialist support that choice. Do not pool species to inflate the sample. No access is yet confirmed and no outreach has been sent for this draft.
2. Ask a qualified avian researcher to revise the codebook, sampling schedule, welfare criteria and feasibility targets. The planning idea of 5–10 households is not a power calculation. Preserve normal routines; no acquisition, isolation, induced distress or automatic playback.
3. Resolve consent, recording rights, human speech/faces, access roles, retention, withdrawal and hosted storage before research collection. The private server remains synthetic-only. A saved app file does not authorize research use.
4. Rehearse with invented audio on actual intended phones. Verify start/stop, 30 seconds of samples, interruption/hidden-page stop, saved WAV readability, permission cancellation and offline reopening. Record device/browser versions. Browser emulation is not this hardware check.
5. After approval, use a prespecified observation schedule, retain quiet windows, record missing/partial windows and document departures. The app's user-selected start is not random sampling. Do not select only interesting calls or extend a window because a preferred behavior appeared.
6. Collect independently reviewable context only through the approved workflow. The current public app records no video. Separate camera files would require an approved synchronization/uncertainty method; matching approximate clock times is insufficient.
7. Have two reviewers assign visible labels without listening to audio, reconcile disagreements only after retaining the original labels, and report agreement, missingness and exclusions. Do not silently turn observer interpretations into ground truth.

## Candidate codebook for specialist revision

| Visible label | Proposed observation rule | What it does not establish |
| --- | --- | --- |
| Moving | Visible locomotion between locations/perches; define minimum movement and interval boundaries before use. | Excitement, anxiety, a request or sound meaning. |
| Feeding | Visible food manipulation/ingestion already occurring naturally; define eligible actions and visibility. | Hunger, preference or a vocal food request. |
| Stationary | Observable animal with no locomotion/feeding under the agreed rules during that interval. | Rest, calmness, silence or absence of communication. |
| Mixed / other / not observable | Changing actions, occlusion, unidentified individual, multiple animals or insufficient evidence. Preserve the reason. | A forced training class or an animal's internal state. |

Labels apply to intervals, not automatically an entire 30-second window. Proposed visible behavior, acoustic source (animal/person/environment/unknown), caller certainty and human-word imitation are distinct annotations. The current Station offers a main-source review and notes, not this full independent video-labeling workflow. Never use the acoustic model to generate its own evaluation labels.

## Go/no-go review

Before modeling, the scientific lead must specify acceptable label agreement, usable duration, missingness and cohort coverage; no arbitrary thresholds or success claims are supplied here. Stop or revise if the camera cannot establish the action/caller, household sound predicts the labels trivially, recordings are unsuitable or the sample cannot support the intended holdout.

Freeze connected household/animal/device/session groups before fitting preprocessing or models. Compare majority, context/timing-only, background-only and acoustic baselines. Evaluate calibration, abstention and failures on unseen groups; keep identity recognition a separate task. Publish the protocol and aggregate feasibility outcomes when reviewed rights permit, including negative findings.

## What this continuation delivers

- A user-started whole-window audio mode that keeps quiet samples, flags incomplete recordings, stops at 30 seconds and exports local WAV plus journal.
- One licensed external budgerigar file inspected for structure; 15 call containers are not 15 independent subjects and do not supply the proposed visible-behavior labels.
- A readiness/codebook draft. Actual carers, scientific reviewer, physical phones, approved synchronized context capture and hosted admission are still required.
