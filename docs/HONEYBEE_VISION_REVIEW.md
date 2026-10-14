# Independent review: honeybee waggle-dance vision

This brief asks for methods review of Talk2Nature's summary of Wario et al. (2017), Automatic detection and decoding of honey bee waggle dances, and the separate 2015 BeesBook engineering comparator. It is a public invitation for critical feedback, not a collaboration, endorsement or claim of independent validation.

## Scope

The 2017 paper describes computer vision for detecting a predefined waggle-run pattern, estimating orientation and duration, and mapping dances to a field location after distance calibration. It reports 90.07% validation accuracy (89.8% recall at 95% precision) from a CNN trained on manually labeled detections. Eight people supplied orientation references for 200 waggle runs. The study's field illustration used one colony and a known artificial feeder.

Talk2Nature reviewed targeted article sections and pinned repository metadata, not the supplementary files or raw samples. The author-linked repository at commit 3aaa5099aac698bd08df1d55f4cd5183d32f7e7d has no recognized license and no LICENSE/COPYING file in its inspected tree. No repository data, code or video was downloaded or run.

## Questions for reviewers

1. Do the reported validation and eight-person angle reference support the limited detection and orientation claims? What uncertainty or evaluation detail should be made clearer?
2. Which held-out unit—colony, day, hive, camera or site—would be necessary before claiming transfer beyond the reported setup?
3. Which frame-rate, spatial-resolution, lighting and calibration constraints are essential? What would a valid phone-camera feasibility test need to measure?
4. What is a useful, passive camera question for animal-communication science that also protects welfare, privacy and sensitive locations?

Please identify your relevant expertise, point to the exact article section or analysis concern, and distinguish a factual correction from a proposed new experiment. Do not attach recordings, private research material, personal information or sensitive wildlife locations. A public reply through the linked GitHub issue form requires GitHub sign-in and will be visible publicly.

## Decision boundary

Until methods and rights are independently reviewed, treat this as a bounded known-signal example. The work does not establish arbitrary gesture understanding, natural-language exchange, consumer-phone performance or a Talk2Nature camera feature. The code and ground-truth data remain metadata-only.
