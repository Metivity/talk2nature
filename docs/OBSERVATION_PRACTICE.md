# Observation practice

Updated October 11, 2026. This is a short educational exercise, not a study, annotation instrument, animal behavior classifier or source of training labels.

## Question and rationale

Can a first-time visitor practice keeping a directly described event separate from a possible explanation and an unresolved claim before opening the observation tools?

The exercise implements the next idea already listed in [the app direction](APP_NEXT_IDEAS.md). It follows the project's existing distinctions in [the researcher starter kit](RESEARCHER_START.md), [open-source reuse boundaries](OPEN_SOURCE.md) and [AutoResearch readiness rules](AUTORESEARCH_ADAPTATION.md): an event report, an interpretation and a prediction are different kinds of statements. The examples are original invented scenarios; no outside paper, recording, model or third-party media informs them.

## Implementation and privacy

The new Field Companion route is `/app/practice/`. It presents three invented scenes: sound without video, a visible turn near a call with unsynchronized clocks, and a parrot repeating a similar-sounding phrase. For each statement, the visitor chooses **Directly observed**, **Possible explanation**, or **Not established** and receives a short rationale tied to the scene. There are no points, leaderboard, animal response, recording, sign-in, analytics, upload, browser storage or private database connection. Choices exist only in the open tab and are discarded when it closes. The optional wording-feedback link opens the existing share page; it does not include the visitor's choices, and posting remains a user action. The practice remains available in the user-requested public-only offline shell.

The scenarios are teaching prompts, not a validated codebook. Their rationale cannot establish what any real animal heard, intended or understood. In particular, temporal proximity does not establish causation, and a repeated sound does not by itself establish comprehension.

## Rights and provenance

All scenario text and the small interaction module are original project material. The software follows the repository's Apache-2.0 license; public original summaries and explanatory copy follow CC BY 4.0. No third-party dataset, audio, article text, image, code or model weights are included. No participant observation is collected or admitted.

## Acceptance and limits

Software acceptance checks cover the three scenes and their evidence categories, accessible button labels and pressed state, per-statement feedback, keyboard focus when changing scenes, narrow layout rules, route generation and exact offline-shell inclusion. The local build and test results are recorded in `STATUS.md`.

No independent first-time user or educator has tried this exercise. Automated checks cannot establish comprehension, teaching value, screen-reader usability or a better quality of future observations. The next decision is to invite a small independent usability review only when outreach is authorized, revise the language from observed feedback, and keep the exercise clearly marked as practice until then. Publication and deployment are separate decisions and are not made by this local milestone.
