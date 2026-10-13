# Independent review: phone recording paths and device variation

**Status:** request for a bounded methods critique; no independent specialist review has been received. This is not an approved protocol, calibration procedure, device recommendation, field study or request for recordings.

## The question

What is the smallest useful, no-animal test of the phone and app recording paths that could inform a future, species-specific bioacoustic workflow? Does such a bench check answer a meaningful question at all, or would it create confidence that does not transfer to field recordings?

## Evidence to assess

- Jäckel et al. (2021), [*Opportunities and limitations: A comparative analysis of citizen science and expert recordings for bioacoustic research*](https://doi.org/10.1371/journal.pone.0253763). The paper compared 5,679 Berlin nightingale citizen-science recordings with expert recordings and ran a controlled playback comparison. Twelve devices were placed together for playback; ten were smartphones. The loudspeaker was set to 74 dB(A) at one metre and placed eight metres from the recorders, but smartphone gain was not standardized. The paper reports device-dependent differences in measured frequency parameters. This is a useful design example, not a ready-made calibration recipe.
- Gili, Bertolino & Rolando (2024), [*Using mobile device built-in microphones to monitor bats*](https://doi.org/10.1007/s10531-024-02818-9). The paper compares built-in phone microphones with bat detectors for selected calls in an 8–24 kHz range. It reports variation by device model, missed calls near the upper detection range and aliasing in five models; its citizen-science pilot covered 35 models and 80 sessions. These results do not validate current devices, browser processing, Talk2Nature capture paths or other taxa.

The [source-linked Talk2Nature evidence note](https://metivity.github.io/talk2nature/research/smartphone-bioacoustics-device-variability/) records the review depth and unresolved file-level questions. No linked audio, dataset archive, article supplement or code was acquired or reproduced.

## Questions for a reviewer

1. Would a no-animal reference test answer a useful prerequisite question for a defined acoustic task, or is it too detached from field conditions to guide the app?
2. Which capture paths should be compared first? The browser Station and native Android Station are different pipelines; iOS Safari and physical-device behavior remain unverified. What source and reference recording would separate microphone, operating-system/browser processing and app settings?
3. What minimum device and session metadata is necessary for reproduction without collecting serial numbers, account identifiers, precise locations or persistent device fingerprints?
4. Which measurements and uncertainty summaries matter for a selected frequency range, and is any pass/fail threshold defensible? If not, what should remain descriptive?
5. What can the app's short input-level check honestly tell a visitor, and what result would change the decision to build a more advanced device-check workflow?

## Boundaries and decision

This review needs no animal, participant or app recording. Do not test playback near wildlife, request private recordings, or interpret a level check as microphone calibration. The issue form is public; do not include personal contact details, unpublished material, raw data or sensitive locations.

If reviewers find a bench test useful, first write a separate, versioned protocol with a defined target task, reference chain, device grouping, uncertainty and data-minimization plan. That would still be a technical characterization, not proof of field suitability or animal-call meaning. If no defensible test can change a product or scientific decision, keep the device-variability caveat and do not add calibration-like UI.

Submit a bounded critique through the [scientific-methods review form](https://github.com/Metivity/talk2nature/issues/new?template=scientific-review.yml). A submitted issue is not itself independent validation; any substantive change will be checked against its cited source and recorded with its review depth.
