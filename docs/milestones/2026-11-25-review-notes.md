# Review notes after recording

The whole-moment workflow now offers **What did you notice?** before Save. This makes it possible to finish a short recording, then describe it in ordinary language. The note uses the existing recording-level review field. Its timing is separate from observations marked during capture. An unsubmitted capture draft still requires deliberate handling and is never silently copied.

Input updates the in-memory review immediately, including when Save is activated before the field loses focus. Editing after a saved-copy acknowledgement hides the stale acknowledgement and prompts a fresh download. Source-label changes preserve the review text. Discarding the session clears the editor. Highlight sessions retain their individual recording notes.

The recap and Compare screen count and label timeline observations and review notes separately. The session format, audio checksums and relative timing remain authoritative for their existing purposes. This feature adds human context, with no inferred animal identity or meaning.

## Verification

All 190 Node tests passed, including new controller regressions for input-before-blur export, source-label changes, saved-copy invalidation and discard cleanup. Local noindex and public builds passed their site checks with 197 routes. In Chrome at 390 × 844 CSS pixels, the new note and Save were visible together after focusing the note. At 320px and 390px the document width matched the viewport.

A two-second invented rehearsal was saved through the native macOS Save dialog and reopened through the native file picker. Its ZIP and Compare screen retained the exact review text, one audio window and zero timeline markers. Browser logs showed no errors. This was desktop Chrome with viewport overrides; named physical phones and independent newcomer acceptance remain pending.

The next usability check is whether an independent first-time user can record the invented example, add a review note, save it and reopen it without instructions about formats or archive contents. See the existing [first-use walkthrough](../FIRST_USE_WALKTHROUGH.md).
